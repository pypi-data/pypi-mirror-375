import os
import sys

import yaml
from mcp.server.fastmcp import FastMCP, Image

from adbdevicemanager import AdbDeviceManager

# Environment variable support
CONFIG_FILE = os.environ.get('ANDROID_MCP_CONFIG', 'config.yaml')
CONFIG_FILE_EXAMPLE = "config.yaml.example"

# Load config (make config file optional)
config = {}
device_name = os.environ.get('ANDROID_DEVICE_SERIAL', None)
auto_start_emulator = os.environ.get('ANDROID_AUTO_START_EMULATOR', 'true').lower() == 'true'

# If device_name not already set by environment variable, try config file
if not device_name and os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f.read()) or {}
        device_config = config.get("device", {})
        configured_device_name = device_config.get(
            "name") if device_config else None
        
        # Check for auto-start emulator setting in config
        if 'auto_start_emulator' in device_config:
            auto_start_emulator = device_config.get('auto_start_emulator', True)

        # Support multiple ways to specify auto-selection:
        # 1. name: null (None in Python)
        # 2. name: "" (empty string)
        # 3. name field completely missing
        if configured_device_name and configured_device_name.strip():
            device_name = configured_device_name.strip()
            print(f"Loaded config from {CONFIG_FILE}")
            print(f"Configured device: {device_name}")
        else:
            print(f"Loaded config from {CONFIG_FILE}")
            print(
                "No device specified in config, will auto-select if only one device connected")
    except Exception as e:
        print(f"Error loading config file {CONFIG_FILE}: {e}", file=sys.stderr)
        print(
            f"Please check the format of your config file or recreate it from {CONFIG_FILE_EXAMPLE}", file=sys.stderr)
        sys.exit(1)
elif device_name:
    print(f"Using device from ANDROID_DEVICE_SERIAL environment variable: {device_name}")
else:
    print(
        f"Config file {CONFIG_FILE} not found, using auto-selection for device")

# Initialize MCP and device manager
# AdbDeviceManager will handle auto-selection if device_name is None
mcp = FastMCP("android")
print(f"Auto-start emulator: {auto_start_emulator}")
deviceManager = AdbDeviceManager(device_name, auto_start_emulator=auto_start_emulator)


@mcp.tool()
def get_packages() -> str:
    """
    Get all installed packages on the device
    Returns:
        str: A list of all installed packages on the device as a string
    """
    result = deviceManager.get_packages()
    return result


@mcp.tool()
def execute_adb_shell_command(command: str) -> str:
    """Executes an ADB command and returns the output or an error.
    Args:
        command (str): The ADB shell command to execute
    Returns:
        str: The output of the ADB command
    """
    result = deviceManager.execute_adb_shell_command(command)
    return result


@mcp.tool()
def get_uilayout() -> str:
    """
    Retrieves information about clickable elements in the current UI.
    Returns a formatted string containing details about each clickable element,
    including its text, content description, bounds, and center coordinates.

    Returns:
        str: A formatted list of clickable elements with their properties
    """
    result = deviceManager.get_uilayout()
    return result


@mcp.tool()
def get_screenshot() -> Image:
    """Takes a screenshot of the device and returns it.
    Returns:
        Image: the screenshot
    """
    deviceManager.take_screenshot()
    return Image(path="compressed_screenshot.png")


@mcp.tool()
def get_package_action_intents(package_name: str) -> list[str]:
    """
    Get all non-data actions from Activity Resolver Table for a package
    Args:
        package_name (str): The name of the package to get actions for
    Returns:
        list[str]: A list of all non-data actions from the Activity Resolver Table for the package
    """
    result = deviceManager.get_package_action_intents(package_name)
    return result


@mcp.tool()
def list_emulators() -> dict:
    """
    List available Android Virtual Devices (AVDs) that can be started.
    Returns:
        dict: Contains 'available' (list of AVD names) and 'command' (emulator command path)
    """
    import subprocess
    
    # Check for emulator command
    emulator_paths = [
        # macOS
        os.path.expanduser("~/Library/Android/sdk/emulator/emulator"),
        "/usr/local/bin/emulator",
        "/opt/homebrew/bin/emulator",
        # Linux
        os.path.expanduser("~/Android/sdk/emulator/emulator"),
        # Windows
        os.path.expanduser("~\\AppData\\Local\\Android\\Sdk\\emulator\\emulator.exe"),
        "C:\\Program Files (x86)\\Android\\android-sdk\\emulator\\emulator.exe",
    ]
    
    emulator_cmd = None
    for path in emulator_paths:
        if os.path.exists(path):
            emulator_cmd = path
            break
    
    if not emulator_cmd:
        try:
            subprocess.run(["emulator", "-version"], 
                         capture_output=True, timeout=2)
            emulator_cmd = "emulator"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"available": [], "command": None, "error": "Emulator not found"}
    
    # List AVDs
    try:
        result = subprocess.run([emulator_cmd, "-list-avds"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            avds = result.stdout.strip().split('\n')
            return {"available": avds, "command": emulator_cmd}
        else:
            return {"available": [], "command": emulator_cmd, "error": "No AVDs found"}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return {"available": [], "command": emulator_cmd, "error": str(e)}


@mcp.tool()
def start_emulator_avd(avd_name: str | None = None, headless: bool = False) -> dict:
    """
    Start an Android emulator with the specified AVD.
    Args:
        avd_name: Name of the AVD to start. If None, uses first available AVD.
        headless: If True, starts emulator without GUI (faster, uses less resources)
    Returns:
        dict: Status information including success, device_serial, and message
    """
    import subprocess
    import time
    
    # Get list of AVDs
    emulator_info = list_emulators()
    if not emulator_info["command"]:
        return {"success": False, "error": "Emulator not found"}
    
    emulator_cmd = emulator_info["command"]
    
    # Auto-select AVD if not specified
    if not avd_name:
        if emulator_info["available"]:
            avd_name = emulator_info["available"][0]
            print(f"Auto-selected AVD: {avd_name}")
        else:
            return {"success": False, "error": "No AVDs available"}
    
    # Check if AVD exists
    if avd_name not in emulator_info["available"]:
        return {
            "success": False, 
            "error": f"AVD '{avd_name}' not found",
            "available": emulator_info["available"]
        }
    
    # Check if emulator is already running
    current_devices = AdbDeviceManager.get_available_devices()
    if any('emulator' in d for d in current_devices):
        return {
            "success": True,
            "message": "Emulator already running",
            "devices": current_devices
        }
    
    # Start emulator
    try:
        cmd = [emulator_cmd, "-avd", avd_name, "-no-snapshot-load"]
        if headless:
            cmd.append("-no-window")
        
        # Start in background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        
        # Wait for device to appear
        print(f"Starting emulator with AVD: {avd_name}...")
        for i in range(60):  # Wait up to 60 seconds
            time.sleep(1)
            devices = AdbDeviceManager.get_available_devices()
            emulator_devices = [d for d in devices if 'emulator' in d]
            if emulator_devices:
                return {
                    "success": True,
                    "device_serial": emulator_devices[0],
                    "message": f"Emulator started successfully",
                    "pid": process.pid
                }
            if i % 10 == 0 and i > 0:
                print(f"Still waiting for emulator... ({i}s)")
        
        return {
            "success": False,
            "error": "Emulator start timeout - it may still be booting",
            "pid": process.pid
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def stop_emulator(device_serial: str | None = None) -> dict:
    """
    Stop a running Android emulator.
    Args:
        device_serial: Serial of the emulator to stop (e.g., 'emulator-5554'). 
                      If None, stops all emulators.
    Returns:
        dict: Status information
    """
    import subprocess
    
    devices = AdbDeviceManager.get_available_devices()
    emulator_devices = [d for d in devices if 'emulator' in d]
    
    if not emulator_devices:
        return {"success": True, "message": "No emulators running"}
    
    stopped = []
    errors = []
    
    for device in emulator_devices:
        if device_serial and device != device_serial:
            continue
        
        try:
            # Send emu kill command via adb
            cmd = ["adb", "-s", device, "emu", "kill"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                stopped.append(device)
            else:
                errors.append(f"{device}: {result.stderr}")
        except Exception as e:
            errors.append(f"{device}: {str(e)}")
    
    if stopped:
        return {
            "success": True,
            "stopped": stopped,
            "message": f"Stopped emulators: {', '.join(stopped)}"
        }
    elif errors:
        return {
            "success": False,
            "errors": errors
        }
    else:
        return {
            "success": True,
            "message": f"No matching emulator found for {device_serial}"
        }


@mcp.tool()
def list_devices() -> dict:
    """
    List all connected Android devices (physical and emulators).
    Returns:
        dict: Contains 'devices' list with device serials and their types
    """
    devices = AdbDeviceManager.get_available_devices()
    
    device_info = []
    for device in devices:
        device_type = "emulator" if "emulator" in device else "physical"
        device_info.append({
            "serial": device,
            "type": device_type
        })
    
    return {
        "count": len(device_info),
        "devices": device_info
    }


def main():
    """Entry point for uvx/pip script execution."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
