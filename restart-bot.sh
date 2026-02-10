#!/bin/bash
# Restart script for USN Telegram Bot

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🔄 Restarting USN Telegram Bot..."
echo ""

docker compose restart bot

sleep 2

echo ""
docker compose ps
echo ""
echo "✅ Bot restarted"
echo "📋 View logs with: docker compose logs -f bot"