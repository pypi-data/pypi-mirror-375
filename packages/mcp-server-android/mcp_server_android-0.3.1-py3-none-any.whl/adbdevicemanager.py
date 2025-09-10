import os
import subprocess
import sys

from PIL import Image as PILImage
from ppadb.client import Client as AdbClient


class AdbDeviceManager:
    def __init__(self, device_name: str | None = None, exit_on_error: bool = True, 
                 auto_start_emulator: bool = True) -> None:
        """
        Initialize the ADB Device Manager

        Args:
            device_name: Optional name/serial of the device to manage.
                         If None, attempts to auto-select if only one device is available.
            exit_on_error: Whether to exit the program if device initialization fails
            auto_start_emulator: Whether to automatically start an emulator if no devices are connected
        """
        if not self.check_adb_installed():
            error_msg = (
                "\n" + "=" * 60 + "\n"
                "ERROR: ADB is not installed or not in PATH\n" +
                "=" * 60 + "\n\n"
                "To install ADB:\n"
                "1. Download: https://developer.android.com/studio/releases/platform-tools\n"
                "2. Extract and add to PATH\n"
                "3. Verify with: adb version\n\n"
                "For macOS with Homebrew: brew install android-platform-tools\n"
                "For Ubuntu/Debian: sudo apt-get install android-tools-adb\n"
            )
            if exit_on_error:
                print(error_msg, file=sys.stderr)
                sys.exit(1)
            else:
                raise RuntimeError(error_msg)

        available_devices = self.get_available_devices()
        if not available_devices:
            # Try to auto-start emulator if enabled
            if auto_start_emulator:
                print("No devices connected. Attempting to start emulator...")
                if self.start_emulator(auto_select=True):
                    # Wait a bit more for device to be fully ready
                    import time
                    time.sleep(3)
                    available_devices = self.get_available_devices()
                    if available_devices:
                        print(f"Emulator started successfully. Available devices: {available_devices}")
                    else:
                        print("Emulator may still be booting. Please wait and try again.")
                else:
                    print("Failed to auto-start emulator.")
            
            # If still no devices after auto-start attempt, show error
            if not available_devices:
                emulator_msg = self._check_emulator_availability()
                error_msg = (
                    "No devices connected. Please:\n"
                    "- Connect a physical device with USB debugging enabled, OR\n"
                    f"{emulator_msg}"
                )
                if exit_on_error:
                    print(error_msg, file=sys.stderr)
                    sys.exit(1)
                else:
                    raise RuntimeError(error_msg)

        selected_device_name: str | None = None

        if device_name:
            if device_name not in available_devices:
                error_msg = f"Device {device_name} not found. Available devices: {available_devices}"
                if exit_on_error:
                    print(error_msg, file=sys.stderr)
                    sys.exit(1)
                else:
                    raise RuntimeError(error_msg)
            selected_device_name = device_name
        else:  # No device_name provided, try auto-selection
            if len(available_devices) == 1:
                selected_device_name = available_devices[0]
                print(
                    f"No device specified, automatically selected: {selected_device_name}")
            elif len(available_devices) > 1:
                error_msg = (
                    f"Multiple devices connected: {available_devices}\n\n"
                    "Specify a device using one of the following:\n"
                    "- Set ANDROID_DEVICE_SERIAL env var\n"
                    f"- Set device.name in {os.environ.get('ANDROID_MCP_CONFIG', 'config.yaml')}\n"
                    "- Disconnect other devices\n"
                )
                if exit_on_error:
                    print(error_msg, file=sys.stderr)
                    sys.exit(1)
                else:
                    raise RuntimeError(error_msg)
            # If len(available_devices) == 0, it's already caught by the earlier check

        # At this point, selected_device_name should always be set due to the logic above
        # Initialize the device
        self.device = AdbClient().device(selected_device_name)

    @staticmethod
    def check_adb_installed() -> bool:
        """Check if ADB is installed on the system."""
        # First try the standard PATH
        try:
            subprocess.run(["adb", "version"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Try common ADB locations across platforms
        common_adb_paths = [
            # Standard system locations (works in Docker/MetaMCP)
            "/usr/local/bin/adb",
            "/usr/bin/adb",
            "/bin/adb",
            # macOS Homebrew
            "/opt/homebrew/bin/adb",
            "/usr/local/opt/android-platform-tools/bin/adb",
            # macOS Android Studio
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            "/Applications/Android Studio.app/Contents/platform-tools/adb",
            # Linux
            os.path.expanduser("~/Android/sdk/platform-tools/adb"),
            "/opt/android-sdk/platform-tools/adb",
            # Windows
            os.path.expanduser("~\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"),
            "C:\\Program Files (x86)\\Android\\android-sdk\\platform-tools\\adb.exe",
            "C:\\Android\\platform-tools\\adb.exe",
        ]
        
        for adb_path in common_adb_paths:
            if os.path.exists(adb_path):
                try:
                    subprocess.run([adb_path, "version"], check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    # If found, add to PATH for this process
                    adb_dir = os.path.dirname(adb_path)
                    current_path = os.environ.get('PATH', '')
                    if adb_dir not in current_path:
                        os.environ['PATH'] = f"{adb_dir}:{current_path}"
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        return False

    @staticmethod
    def get_available_devices() -> list[str]:
        """Get a list of available devices."""
        return [device.serial for device in AdbClient().devices()]
    
    @staticmethod
    def _check_emulator_availability() -> str:
        """Check if Android emulator is available and list AVDs."""
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
            # Try from PATH
            try:
                result = subprocess.run(["emulator", "-list-avds"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    emulator_cmd = "emulator"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        if not emulator_cmd:
            return "- Install Android Studio and create an AVD (Android Virtual Device)"
        
        # List available AVDs
        try:
            result = subprocess.run([emulator_cmd, "-list-avds"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                avds = result.stdout.strip().split('\n')
                avd_list = ', '.join(avds[:3])  # Show first 3 AVDs
                if len(avds) > 3:
                    avd_list += f" (and {len(avds) - 3} more)"
                return f"- Start an emulator: {emulator_cmd} -avd <name>\n  Available AVDs: {avd_list}"
            else:
                return "- Create an AVD in Android Studio, then start with: emulator -avd <name>"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return "- Create and start an Android emulator"
    
    @staticmethod
    def start_emulator(avd_name: str | None = None, auto_select: bool = True) -> bool:
        """Try to start an Android emulator.
        
        Args:
            avd_name: Specific AVD to start. If None and auto_select=True, uses first available.
            auto_select: If True and avd_name is None, automatically selects first AVD.
            
        Returns:
            True if emulator started successfully, False otherwise.
        """
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
                return False
        
        # Get list of AVDs if needed
        if not avd_name and auto_select:
            try:
                result = subprocess.run([emulator_cmd, "-list-avds"],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    avds = result.stdout.strip().split('\n')
                    avd_name = avds[0]  # Use first AVD
                    print(f"Auto-selected AVD: {avd_name}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return False
        
        if not avd_name:
            return False
        
        # Start emulator in background
        try:
            # Use -no-window for headless mode, remove if you want GUI
            cmd = [emulator_cmd, "-avd", avd_name, "-no-snapshot-load"]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print(f"Starting emulator with AVD: {avd_name}")
            print("Waiting for emulator to boot (this may take 30-60 seconds)...")
            
            # Wait for device to appear in ADB
            import time
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)
                devices = AdbDeviceManager.get_available_devices()
                if any('emulator' in d for d in devices):
                    print(f"Emulator started successfully: {devices}")
                    return True
                if i % 10 == 0:
                    print(f"Still waiting for emulator... ({i}s)")
            
            print("Emulator start timeout - it may still be booting")
            return False
            
        except Exception as e:
            print(f"Failed to start emulator: {e}")
            return False

    def get_packages(self) -> str:
        command = "pm list packages"
        packages = self.device.shell(command).strip().split("\n")
        result = [package[8:] for package in packages]
        output = "\n".join(result)
        return output

    def get_package_action_intents(self, package_name: str) -> list[str]:
        command = f"dumpsys package {package_name}"
        output = self.device.shell(command)

        resolver_table_start = output.find("Activity Resolver Table:")
        if resolver_table_start == -1:
            return []
        resolver_section = output[resolver_table_start:]

        non_data_start = resolver_section.find("\n  Non-Data Actions:")
        if non_data_start == -1:
            return []

        section_end = resolver_section[non_data_start:].find("\n\n")
        if section_end == -1:
            non_data_section = resolver_section[non_data_start:]
        else:
            non_data_section = resolver_section[
                non_data_start: non_data_start + section_end
            ]

        actions = []
        for line in non_data_section.split("\n"):
            line = line.strip()
            if line.startswith("android.") or line.startswith("com."):
                actions.append(line)

        return actions

    def execute_adb_shell_command(self, command: str) -> str:
        """Executes an ADB command and returns the output."""
        if command.startswith("adb shell "):
            command = command[10:]
        elif command.startswith("adb "):
            command = command[4:]
        result = self.device.shell(command)
        return result

    def take_screenshot(self) -> None:
        self.device.shell("screencap -p /sdcard/screenshot.png")
        self.device.pull("/sdcard/screenshot.png", "screenshot.png")
        self.device.shell("rm /sdcard/screenshot.png")

        # compressing the ss to avoid "maximum call stack exceeded" error on claude desktop
        with PILImage.open("screenshot.png") as img:
            width, height = img.size
            new_width = int(width * 0.3)
            new_height = int(height * 0.3)
            resized_img = img.resize(
                (new_width, new_height), PILImage.Resampling.LANCZOS
            )

            resized_img.save(
                "compressed_screenshot.png", "PNG", quality=85, optimize=True
            )

    def get_uilayout(self) -> str:
        self.device.shell("uiautomator dump")
        self.device.pull("/sdcard/window_dump.xml", "window_dump.xml")
        self.device.shell("rm /sdcard/window_dump.xml")

        import re
        import xml.etree.ElementTree as ET

        def calculate_center(bounds_str):
            matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
            if len(matches) == 2:
                x1, y1 = map(int, matches[0])
                x2, y2 = map(int, matches[1])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                return center_x, center_y
            return None

        tree = ET.parse("window_dump.xml")
        root = tree.getroot()

        clickable_elements = []
        for element in root.findall(".//node[@clickable='true']"):
            text = element.get("text", "")
            content_desc = element.get("content-desc", "")
            bounds = element.get("bounds", "")

            # Only include elements that have either text or content description
            if text or content_desc:
                center = calculate_center(bounds)
                element_info = "Clickable element:"
                if text:
                    element_info += f"\n  Text: {text}"
                if content_desc:
                    element_info += f"\n  Description: {content_desc}"
                element_info += f"\n  Bounds: {bounds}"
                if center:
                    element_info += f"\n  Center: ({center[0]}, {center[1]})"
                clickable_elements.append(element_info)

        if not clickable_elements:
            return "No clickable elements found with text or description"
        else:
            result = "\n\n".join(clickable_elements)
            return result
