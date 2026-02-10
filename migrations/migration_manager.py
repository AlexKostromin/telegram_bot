"""
Migration manager for database schema management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from pathlib import Path


class MigrationHistory:
    """Table for tracking applied migrations."""

    @staticmethod
    async def create_table(session: AsyncSession):
        """Create migration_history table (database-agnostic)."""
        from config import DB_TYPE

        if DB_TYPE == "postgresql":
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:  # SQLite
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

        await session.commit()


class MigrationManager:
    """Manager for running database migrations."""

    def __init__(self, engine, session_maker: sessionmaker):
        """Initialize migration manager."""
        self.engine = engine
        self.session_maker = session_maker
        self.migrations_dir = Path(__file__).parent

    async def create_migration_table(self):
        """Create migration history table."""
        async with self.session_maker() as session:
            await MigrationHistory.create_table(session)

    async def get_applied_migrations(self) -> list:
        """Get list of applied migration versions."""
        async with self.session_maker() as session:
            result = await session.execute(text("""
                SELECT version FROM migration_history ORDER BY applied_at
            """))
            migrations = result.scalars().all()
            return list(migrations)

    async def mark_migration_applied(self, version: str):
        """Mark migration as applied."""
        async with self.session_maker() as session:
            await session.execute(text("""
                INSERT INTO migration_history (version, applied_at)
                VALUES (:version, :applied_at)
            """), {
                "version": version,
                "applied_at": datetime.utcnow()
            })
            await session.commit()

    async def run_migrations(self):
        """Run all unapplied migrations."""
        # Create migration history table if it doesn't exist
        await self.create_migration_table()

        applied = await self.get_applied_migrations()

        # Get all migration files
        migration_files = sorted([
            f for f in os.listdir(self.migrations_dir)
            if f.startswith('00') and f.endswith('.py') and f != 'migration_manager.py'
        ])

        async with self.session_maker() as session:
            for migration_file in migration_files:
                version = migration_file.replace('.py', '')

                if version in applied:
                    print(f"⏭️  Migration {version} already applied, skipping...")
                    continue

                print(f"🔄 Running migration {version}...")

                try:
                    # Import and run migration
                    module_name = f"migrations.{version}"
                    import importlib
                    migration_module = importlib.import_module(module_name)

                    if hasattr(migration_module, 'migrate'):
                        await migration_module.migrate(session)

                    await self.mark_migration_applied(version)
                    print(f"✅ Migration {version} applied successfully!")

                except Exception as e:
                    print(f"❌ Error running migration {version}: {str(e)}")
                    raise
