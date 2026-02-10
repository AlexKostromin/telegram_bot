#!/bin/bash
# Stop script for USN Telegram Bot

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🛑 Stopping USN Telegram Bot..."
echo ""

docker compose stop

sleep 1

echo ""
echo "✅ Bot stopped"
echo ""
echo "To remove containers completely, run: docker compose down"
echo "To remove containers and database, run: docker compose down -v"