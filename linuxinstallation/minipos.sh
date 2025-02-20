#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Start the Ngrok and Python scripts in the background
nohup "$SCRIPT_DIR/minipos_start.sh" &> /dev/null &
sleep 1
nohup "$SCRIPT_DIR/ngrokconnection.sh" &> /dev/null &

# Wait for a short time to ensure they are up
sleep 4

exit