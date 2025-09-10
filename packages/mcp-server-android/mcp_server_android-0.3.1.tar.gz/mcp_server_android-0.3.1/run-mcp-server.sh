#!/bin/bash
# Android MCP Server wrapper script for MetaMCP
# This script handles spaces in the directory path

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set up environment
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PYTHONPATH="$SCRIPT_DIR"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the server using uv
exec uv run server.py
