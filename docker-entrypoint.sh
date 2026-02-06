#!/bin/bash
# Docker entrypoint script for USN Telegram Bot

set -e

echo "=========================================="
echo "USN Telegram Bot - Docker Entrypoint"
echo "=========================================="

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN is not set!"
    echo "Please set BOT_TOKEN in your .env file"
    exit 1
fi

echo "✓ BOT_TOKEN is configured"
echo "✓ DEBUG: ${DEBUG:-False}"
echo "✓ LOGGING_LEVEL: ${LOGGING_LEVEL:-INFO}"

# Create data directory if it doesn't exist
mkdir -p /data /app/logs

echo "✓ Directories ready"

# Run the bot
echo "=========================================="
echo "Starting Telegram Bot..."
echo "=========================================="
exec python main.py