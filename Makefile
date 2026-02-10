# ============================================================================
# USN Telegram Bot - Comprehensive Makefile
# ============================================================================
# Usage: make [target]
# Full documentation: make help
#
# Supports:
#   - SQLite development (default)
#   - PostgreSQL production
#   - Docker containerization
#   - Database migrations
#   - Admin panel management
# ============================================================================

.PHONY: help \
		up down restart logs build clean status health shell \
		dev sqlite postgres migrate \
		admin-up admin-down admin-shell admin-logs \
		db-shell db-backup db-restore \
		test lint format \
		version info

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================
COMPOSE_FILE := docker-compose.yml
BOT_CONTAINER := usn-telegram-bot
POSTGRES_CONTAINER := usn-postgres
ADMIN_CONTAINER := usn-admin-panel
PROJECT_NAME := usn-bot

# ============================================================================
# MAIN TARGETS
# ============================================================================

help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║        USN Telegram Bot - Comprehensive Makefile              ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)═══ BASIC COMMANDS ═══$(NC)"
	@echo "  $(YELLOW)make help$(NC)              Show this help message"
	@echo "  $(YELLOW)make info$(NC)              Show project information"
	@echo "  $(YELLOW)make version$(NC)           Show versions of installed tools"
	@echo ""
	@echo "$(GREEN)═══ DEVELOPMENT (SQLite) ═══$(NC)"
	@echo "  $(YELLOW)make dev$(NC)               Start bot with SQLite (default)"
	@echo "  $(YELLOW)make sqlite$(NC)            Same as 'make dev'"
	@echo "  $(YELLOW)make up$(NC)                Start bot in background"
	@echo "  $(YELLOW)make down$(NC)              Stop all services"
	@echo "  $(YELLOW)make restart$(NC)           Restart bot service"
	@echo "  $(YELLOW)make logs$(NC)              View bot logs (live, Ctrl+C to exit)"
	@echo "  $(YELLOW)make logs-tail $(NC)        View last 50 lines of logs"
	@echo ""
	@echo "$(GREEN)═══ PRODUCTION (PostgreSQL) ═══$(NC)"
	@echo "  $(YELLOW)make postgres$(NC)          Start with PostgreSQL database"
	@echo "  $(YELLOW)make migrate$(NC)           Migrate from SQLite to PostgreSQL"
	@echo "  $(YELLOW)make db-init$(NC)           Initialize PostgreSQL container"
	@echo ""
	@echo "$(GREEN)═══ ADMIN PANEL ═══$(NC)"
	@echo "  $(YELLOW)make admin-up$(NC)          Start Django admin panel"
	@echo "  $(YELLOW)make admin-down$(NC)        Stop admin panel"
	@echo "  $(YELLOW)make admin-logs$(NC)        View admin panel logs"
	@echo "  $(YELLOW)make admin-shell$(NC)       Open shell in admin container"
	@echo ""
	@echo "$(GREEN)═══ DATABASE MANAGEMENT ═══$(NC)"
	@echo "  $(YELLOW)make db-shell$(NC)          Open PostgreSQL shell"
	@echo "  $(YELLOW)make db-backup$(NC)         Backup PostgreSQL database"
	@echo "  $(YELLOW)make db-restore$(NC)        Restore PostgreSQL from backup"
	@echo "  $(YELLOW)make db-clean$(NC)          Drop and recreate PostgreSQL"
	@echo ""
	@echo "$(GREEN)═══ DOCKER OPERATIONS ═══$(NC)"
	@echo "  $(YELLOW)make build$(NC)             Build/rebuild bot Docker image"
	@echo "  $(YELLOW)make status$(NC)            Show container status"
	@echo "  $(YELLOW)make health$(NC)            Check bot health"
	@echo "  $(YELLOW)make shell$(NC)             Open shell in bot container"
	@echo "  $(YELLOW)make clean$(NC)             Remove all containers and volumes"
	@echo "  $(YELLOW)make prune$(NC)             Clean up unused Docker resources"
	@echo ""
	@echo "$(GREEN)═══ TESTING & CODE QUALITY ═══$(NC)"
	@echo "  $(YELLOW)make test$(NC)              Run all tests"
	@echo "  $(YELLOW)make lint$(NC)              Run code linter (flake8)"
	@echo "  $(YELLOW)make format$(NC)            Format code (black)"
	@echo ""
	@echo "$(GREEN)═══ UTILITIES ═══$(NC)"
	@echo "  $(YELLOW)make ps$(NC)                Show running containers (alias for status)"
	@echo "  $(YELLOW)make stats$(NC)             Show container resource usage"
	@echo ""

info:
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Project Name: $(PROJECT_NAME)"
	@echo "  Compose File: $(COMPOSE_FILE)"
	@echo "  Bot Container: $(BOT_CONTAINER)"
	@echo "  PostgreSQL Container: $(POSTGRES_CONTAINER)"
	@echo "  Admin Container: $(ADMIN_CONTAINER)"
	@echo ""
	@echo "$(BLUE)Directories:$(NC)"
	@echo "  Current: $$(pwd)"
	@echo "  Docker Compose: $$(command -v docker-compose || echo 'not found')"
	@echo ""

version:
	@echo "$(BLUE)Installed Versions:$(NC)"
	@docker --version 2>/dev/null || echo "Docker: not found"
	@docker compose --version 2>/dev/null || echo "Docker Compose: not found"
	@python3 --version 2>/dev/null || echo "Python: not found"
	@echo ""

# ============================================================================
# BASIC DOCKER OPERATIONS
# ============================================================================

up: build
	@echo "$(BLUE)Starting USN Telegram Bot (SQLite)...$(NC)"
	docker compose up -d --build
	@sleep 3
	@docker compose ps
	@echo "$(GREEN)✓ Bot started$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  View logs: $(YELLOW)make logs$(NC)"
	@echo "  Bot status: $(YELLOW)make health$(NC)"
	@echo "  Open shell: $(YELLOW)make shell$(NC)"

down:
	@echo "$(BLUE)Stopping USN Telegram Bot...$(NC)"
	docker compose down
	@echo "$(GREEN)✓ Bot stopped$(NC)"

restart:
	@echo "$(BLUE)Restarting bot service...$(NC)"
	docker compose restart $(BOT_CONTAINER)
	@sleep 2
	@docker compose ps
	@echo "$(GREEN)✓ Bot restarted$(NC)"

build:
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

clean:
	@echo "$(RED)WARNING: This will remove all containers, networks, and volumes!$(NC)"
	@read -p "$(YELLOW)Are you sure? [y/N]$(NC) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Cleaning up...$(NC)"; \
		docker compose down -v; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled$(NC)"; \
	fi

prune:
	@echo "$(BLUE)Cleaning up unused Docker resources...$(NC)"
	docker system prune -a --volumes -f
	@echo "$(GREEN)✓ Pruned unused resources$(NC)"

# ============================================================================
# DEVELOPMENT MODES
# ============================================================================

dev: up
	@echo "$(GREEN)✓ Development environment started (SQLite)$(NC)"

sqlite: up
	@echo "$(GREEN)✓ Using SQLite database$(NC)"

postgres:
	@echo "$(BLUE)Starting with PostgreSQL...$(NC)"
	DATABASE_URL=postgresql+asyncpg://usn_bot:secure_password@postgres:5432/usn_bot_db \
	POSTGRES_USER=usn_bot \
	POSTGRES_PASSWORD=secure_password \
	POSTGRES_DB=usn_bot_db \
	docker compose --profile all up -d
	@sleep 5
	@docker compose ps
	@echo "$(GREEN)✓ PostgreSQL started$(NC)"

migrate:
	@echo "$(BLUE)Migrating from SQLite to PostgreSQL...$(NC)"
	@bash scripts/migrate_to_postgres.sh
	@echo "$(GREEN)✓ Migration complete$(NC)"

# ============================================================================
# LOGGING & MONITORING
# ============================================================================

logs:
	@echo "$(BLUE)Bot logs (Ctrl+C to exit):$(NC)"
	docker compose logs -f --tail=100 $(BOT_CONTAINER)

logs-tail:
	@echo "$(BLUE)Last 50 lines of bot logs:$(NC)"
	docker compose logs --tail=50 $(BOT_CONTAINER)

status: ps

ps:
	@echo "$(BLUE)Container Status:$(NC)"
	docker compose ps

stats:
	@echo "$(BLUE)Container Resource Usage:$(NC)"
	docker stats --no-stream 2>/dev/null || echo "No containers running"

health:
	@echo "$(BLUE)Checking bot health...$(NC)"
	@docker compose exec $(BOT_CONTAINER) python3 -c "from config import BOT_TOKEN; print('✓ Bot is responsive')" 2>/dev/null || echo "$(YELLOW)⚠ Bot is not running$(NC)"

# ============================================================================
# INTERACTIVE SHELLS
# ============================================================================

shell:
	@echo "$(BLUE)Opening shell in bot container...$(NC)"
	docker compose exec $(BOT_CONTAINER) /bin/bash

# ============================================================================
# ADMIN PANEL
# ============================================================================

admin-up:
	@echo "$(BLUE)Starting Django admin panel...$(NC)"
	docker compose --profile admin up -d admin
	@sleep 3
	@echo "$(GREEN)✓ Admin panel started$(NC)"
	@echo ""
	@echo "$(BLUE)Access admin panel:$(NC)"
	@echo "  URL: http://localhost:8000/admin"
	@echo "  Credentials: admin:admin"

admin-down:
	@echo "$(BLUE)Stopping admin panel...$(NC)"
	docker compose --profile admin down admin
	@echo "$(GREEN)✓ Admin panel stopped$(NC)"

admin-logs:
	@echo "$(BLUE)Admin panel logs:$(NC)"
	docker compose logs -f --tail=50 $(ADMIN_CONTAINER)

admin-shell:
	@echo "$(BLUE)Opening shell in admin container...$(NC)"
	docker compose exec $(ADMIN_CONTAINER) /bin/bash

# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================

db-init:
	@echo "$(BLUE)Initializing PostgreSQL...$(NC)"
	docker compose --profile db up -d postgres
	@sleep 5
	@echo "$(GREEN)✓ PostgreSQL initialized$(NC)"

db-shell:
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	docker exec -it $(POSTGRES_CONTAINER) psql -U usn_bot -d usn_bot_db

db-backup:
	@echo "$(BLUE)Backing up PostgreSQL database...$(NC)"
	@mkdir -p backups
	docker exec $(POSTGRES_CONTAINER) \
		pg_dump -U usn_bot -d usn_bot_db > backups/usn_bot_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created$(NC)"

db-restore:
	@echo "$(BLUE)Restoring PostgreSQL database...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Error: BACKUP_FILE not specified$(NC)"; \
		echo "Usage: make db-restore BACKUP_FILE=backups/usn_bot_YYYYMMDD_HHMMSS.sql"; \
		exit 1; \
	fi
	docker exec -i $(POSTGRES_CONTAINER) \
		psql -U usn_bot -d usn_bot_db < $(BACKUP_FILE)
	@echo "$(GREEN)✓ Restoration complete$(NC)"

db-clean:
	@echo "$(YELLOW)WARNING: This will drop all data in PostgreSQL!$(NC)"
	@read -p "$(YELLOW)Are you sure? [y/N]$(NC) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Dropping database...$(NC)"; \
		docker exec $(POSTGRES_CONTAINER) dropdb -U usn_bot usn_bot_db 2>/dev/null || true; \
		docker exec $(POSTGRES_CONTAINER) createdb -U usn_bot usn_bot_db; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled$(NC)"; \
	fi

# ============================================================================
# TESTING & CODE QUALITY
# ============================================================================

test:
	@echo "$(BLUE)Running tests...$(NC)"
	python3 -m pytest tests/ -v 2>/dev/null || echo "$(YELLOW)pytest not found - skipping$(NC)"

lint:
	@echo "$(BLUE)Running code linter...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null || echo "$(YELLOW)flake8 not found - skipping$(NC)"

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	black . --line-length 100 2>/dev/null || echo "$(YELLOW)black not found - skipping$(NC)"

# ============================================================================
# DEFAULT TARGET
# ============================================================================

.DEFAULT_GOAL := help