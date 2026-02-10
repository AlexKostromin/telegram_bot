"""
Migration 002: Add new fields to users table.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate(session: AsyncSession):
    """
    Add new columns to users table:
    - bio: TEXT NULL
    - date_of_birth: DATE NULL
    - channel_name: VARCHAR(255) NULL
    """
    try:
        result = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        columns = {row[0] for row in result.fetchall()}

        columns_to_add = [
            ("bio", "TEXT NULL"),
            ("date_of_birth", "DATE NULL"),
            ("channel_name", "VARCHAR(255) NULL"),
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                await session.execute(text(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                ))

        await session.commit()
    except Exception as e:
        print(f"  ⚠️  Migration 002: {e}")
        await session.commit()
