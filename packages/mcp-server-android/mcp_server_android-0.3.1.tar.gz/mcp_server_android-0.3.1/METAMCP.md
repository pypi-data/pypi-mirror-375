# MetaMCP Setup Guide

## Quick Setup

Add this configuration to your MetaMCP settings:

```json
{
  "mcpServers": {
    "android": {
      "command": "/Users/vinhlekhanh/Library/Mobile Documents/com~apple~CloudDocs/AI/mcp/server/android-mcp-server/run-mcp-server.sh"
    }
  }
}
```

## Alternative Setup (Using Symlink)

If you prefer to avoid spaces in paths:

```json
{
  "mcpServers": {
    "android": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/vinhlekhanh/android-mcp-server",
        "run",
        "server.py"
      ],
      "env": {
        "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

## Requirements

- ADB installed via Homebrew: `brew install android-platform-tools`
- UV package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Python 3.11+

## Troubleshooting

If you encounter issues:

1. Ensure ADB is accessible: `/usr/local/bin/adb devices`
2. Check the wrapper script is executable: `chmod +x run-mcp-server.sh`
3. Verify the symlink exists: `ls -la ~/android-mcp-server`

For detailed setup instructions and additional configurations, see the `metamcp-setup/` directory.
