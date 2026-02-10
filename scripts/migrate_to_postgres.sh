#!/bin/bash
set -e

echo "=== USN Bot: SQLite -> PostgreSQL Migration ==="

# Create backups directory
mkdir -p backups

# Backup SQLite
if [ -f "bot_database.db" ]; then
    echo "Step 1: Backing up SQLite..."
    cp bot_database.db "backups/sqlite_$(date +%Y%m%d_%H%M%S).db"
    echo "✅ SQLite backup created"
else
    echo "⚠️  No existing SQLite database found (fresh install)"
fi

# Start PostgreSQL
echo "Step 2: Starting PostgreSQL..."
docker compose up -d postgres
sleep 15

# Check PostgreSQL health
echo "Step 3: Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec usn-postgres pg_isready -U ${POSTGRES_USER:-usn_bot} > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ PostgreSQL failed to start within timeout"
    exit 1
fi

# Initialize PostgreSQL database
echo "Step 4: Initializing PostgreSQL database..."
export DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER:-usn_bot}:${POSTGRES_PASSWORD:-secure_password}@localhost:5432/${POSTGRES_DB:-usn_bot_db}"

# Create a simple Python script to test connection and initialize
python3 << 'PYTHON_EOF'
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def init():
    from utils.database import db_manager
    try:
        await db_manager.init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise

try:
    asyncio.run(init())
except Exception as e:
    sys.exit(1)
PYTHON_EOF

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

# Verify PostgreSQL
echo "Step 5: Verifying PostgreSQL..."
docker exec usn-postgres psql -U ${POSTGRES_USER:-usn_bot} -d ${POSTGRES_DB:-usn_bot_db} -c "SELECT count(*) as tables FROM information_schema.tables WHERE table_schema='public'" || {
    echo "❌ Failed to verify PostgreSQL"
    exit 1
}

echo ""
echo "✅ Migration to PostgreSQL completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Update your .env file to use PostgreSQL (already set in docker-compose.yml)"
echo "  2. Start the bot with: docker compose up bot"
echo "  3. Verify bot logs: docker compose logs bot"
echo ""
echo "To verify data:"
echo "  docker exec -it usn-postgres psql -U usn_bot -d usn_bot_db"
echo "  SELECT * FROM users;"
echo ""
