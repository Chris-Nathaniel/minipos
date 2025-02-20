#!/bin/bash

set -e  # Exit on error

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Installing Python..."
    sudo apt update && sudo apt install -y python3 python3-pip
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Pip is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Check if SQLite3 is installed
if ! command -v sqlite3 &> /dev/null; then
    echo "SQLite3 is not installed. Installing..."
    sudo apt update && sudo apt install -y sqlite3
else
    echo "SQLite3 is already installed."
fi

# Verify installation
sqlite3 --version

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt file not found."
    exit 1
fi

# Install required Python packages
echo "Installing required packages from requirements.txt..."
pip3 install -r requirements.txt

echo "All packages installed successfully!"

# Create a desktop shortcut
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_FILE="$SCRIPT_DIR/Minipos.sh"
SHORTCUT_PATH="$HOME/Desktop/Minipos.desktop"
ICON_FILE="$SCRIPT_DIR/icon.ico"

# Check if the icon file exists
if [ ! -f "$ICON_FILE" ]; then
    echo "Warning: icon.ico not found! Using default icon."
    ICON_FILE=""
else
    echo "Using custom icon: $ICON_FILE"
fi

# Create the shortcut file
cat > "$SHORTCUT_PATH" <<EOL
[Desktop Entry]
Type=Application
Name=Minipos
Exec=$TARGET_FILE
Icon=$ICON_FILE
Terminal=true
EOL

chmod +x "$SHORTCUT_PATH"
echo "Shortcut created at $SHORTCUT_PATH"

# Create a fresh database
nohup bash "$SCRIPT_DIR/dbgenerator.sh" &

echo "Setup completed."
exit 0
