"""
Migration 004: Add status and approval tracking to registrations table.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate(session: AsyncSession):
    """
    Add columns to registrations table:
    - status: VARCHAR(20) DEFAULT 'pending' (pending, approved, rejected)
    - confirmed_at: DATETIME NULL
    - confirmed_by: BIGINT NULL (admin telegram_id)

    And set existing confirmed registrations to 'approved' status.

    Safe on fresh installs - columns are already created via models.
    """
    try:
        result = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'registrations'
        """))
        columns = {row[0] for row in result.fetchall()}

        columns_to_add = [
            ("status", "VARCHAR(20) DEFAULT 'pending'"),
            ("confirmed_at", "TIMESTAMP NULL"),
            ("confirmed_by", "BIGINT NULL"),
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                await session.execute(text(
                    f"ALTER TABLE registrations ADD COLUMN {column_name} {column_def}"
                ))

        # Update existing confirmed registrations
        try:
            await session.execute(text("""
                UPDATE registrations
                SET status = 'approved', confirmed_at = created_at
                WHERE is_confirmed = 1
            """))
        except Exception:
            pass  # No data yet

        await session.commit()
    except Exception as e:
        print(f"  ⚠️  Migration 004: {e}")
        await session.commit()
