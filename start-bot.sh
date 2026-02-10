#!/bin/bash
# Quick start script for USN Telegram Bot

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting USN Telegram Bot..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your BOT_TOKEN"
    echo "📝 Editor: nano .env"
    exit 1
fi

# Check if BOT_TOKEN is set
if grep -q "BOT_TOKEN=YOUR_BOT_TOKEN_HERE" .env; then
    echo "❌ Please set your BOT_TOKEN in .env file!"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    exit 1
fi

echo "✓ Docker Compose found: $(docker compose --version)"
echo ""

# Start containers
echo "📦 Building and starting containers..."
docker compose up -d --build

sleep 2

# Show status
echo ""
echo "✅ Bot is starting..."
echo ""
docker compose ps
echo ""
echo "📋 View logs with: docker compose logs -f bot"
echo "🛑 Stop bot with: docker compose down"