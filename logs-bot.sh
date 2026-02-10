#!/bin/bash
# View logs for USN Telegram Bot

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "📋 USN Telegram Bot Logs (following live output)"
echo "Press Ctrl+C to exit"
echo ""

docker compose logs -f --tail=100 bot