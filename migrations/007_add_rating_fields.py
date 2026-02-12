"""
Migration 007: Add game rating fields to users table and make country nullable.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate(session: AsyncSession):
    """
    Add columns to users table:
    - classic_rating: INTEGER NULL
    - quick_rating: INTEGER NULL
    - team_rating: INTEGER NULL
    Also make country nullable.
    """
    try:
        result = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        columns = {row[0] for row in result.fetchall()}

        columns_to_add = [
            ("classic_rating", "INTEGER NULL"),
            ("quick_rating", "INTEGER NULL"),
            ("team_rating", "INTEGER NULL"),
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                await session.execute(text(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                ))

        await session.execute(text(
            "ALTER TABLE users ALTER COLUMN country DROP NOT NULL"
        ))

        await session.commit()
    except Exception as e:
        print(f"  ⚠️  Migration 007: {e}")
        await session.commit()
