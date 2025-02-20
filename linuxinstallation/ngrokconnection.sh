#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NGROK_PATH="$SCRIPT_DIR/ngrok"

# Load .env variables
NGROK_AUTH=$(grep 'NGROK_AUTH' .env | cut -d '=' -f2 | tr -d '[:space:]')
NGROK_DOMAIN=$(grep 'NGROK_DOMAIN' .env | cut -d '=' -f2 | tr -d '[:space:]')

# Display loaded values for debugging
echo "NGROK_DOMAIN=$NGROK_DOMAIN"
echo "NGROK_AUTH=$NGROK_AUTH"

# Authenticate with ngrok
"$NGROK_PATH" authtoken "$NGROK_AUTH"

# Start ngrok with the specified domain and port
"$NGROK_PATH" http --domain="$NGROK_DOMAIN" 5000 & disown

exit 0
