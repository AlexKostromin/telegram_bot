.PHONY: help up down restart logs build clean status health shell

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m # No Color

help:
	@echo "$(BLUE)USN Telegram Bot - Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  make up         - Start the bot"
	@echo "  make down       - Stop the bot"
	@echo "  make restart    - Restart the bot"
	@echo "  make logs       - View bot logs (live)"
	@echo "  make build      - Build/rebuild Docker image"
	@echo "  make status     - Show container status"
	@echo "  make health     - Check bot health"
	@echo "  make shell      - Open shell in bot container"
	@echo "  make clean      - Stop and remove all containers, networks and volumes"
	@echo "  make prod-up    - Start bot in production mode"
	@echo ""

up:
	@echo "$(BLUE)Starting USN Telegram Bot...$(NC)"
	docker compose up -d --build
	@sleep 2
	@docker compose ps
	@echo "$(GREEN)✓ Bot started$(NC)"

down:
	@echo "$(BLUE)Stopping USN Telegram Bot...$(NC)"
	docker compose down
	@echo "$(GREEN)✓ Bot stopped$(NC)"

restart:
	@echo "$(BLUE)Restarting USN Telegram Bot...$(NC)"
	docker compose restart bot
	@sleep 2
	@docker compose ps
	@echo "$(GREEN)✓ Bot restarted$(NC)"

logs:
	@echo "$(BLUE)Bot logs (press Ctrl+C to exit)$(NC)"
	docker compose logs -f --tail=100 bot

build:
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

status:
	@echo "$(BLUE)Container status:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)Resource usage:$(NC)"
	@docker stats --no-stream usn-telegram-bot || echo "Container not running"

health:
	@echo "$(BLUE)Checking bot health...$(NC)"
	@docker compose exec bot python -c "print('✓ Bot is responsive')" 2>/dev/null || echo "$(YELLOW)⚠ Bot is not running or not responding$(NC)"

shell:
	@echo "$(BLUE)Opening shell in bot container...$(NC)"
	docker compose exec bot /bin/bash

clean:
	@echo "$(YELLOW)WARNING: This will remove all containers, networks, and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Cleaning up...$(NC)"; \
		docker compose down -v; \
		docker system prune -a -f; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	fi

prod-up:
	@echo "$(BLUE)Starting bot in PRODUCTION mode...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
	@sleep 2
	@docker compose ps
	@echo "$(GREEN)✓ Bot started in production mode$(NC)"

.DEFAULT_GOAL := help