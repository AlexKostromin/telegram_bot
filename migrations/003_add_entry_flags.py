"""
Migration 003: Add role-specific entry flags to competitions table.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate(session: AsyncSession):
    """
    Add columns to competitions table:
    - player_entry_open: BOOLEAN DEFAULT TRUE
    - voter_entry_open: BOOLEAN DEFAULT TRUE
    - viewer_entry_open: BOOLEAN DEFAULT TRUE
    - adviser_entry_open: BOOLEAN DEFAULT TRUE
    - requires_time_slots: BOOLEAN DEFAULT FALSE
    - requires_jury_panel: BOOLEAN DEFAULT FALSE

    Safe on fresh installs - columns are already created via models.
    """
    try:
        result = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'competitions'
        """))
        columns = {row[0] for row in result.fetchall()}

        columns_to_add = [
            ("player_entry_open", "BOOLEAN DEFAULT TRUE"),
            ("voter_entry_open", "BOOLEAN DEFAULT TRUE"),
            ("viewer_entry_open", "BOOLEAN DEFAULT TRUE"),
            ("adviser_entry_open", "BOOLEAN DEFAULT TRUE"),
            ("requires_time_slots", "BOOLEAN DEFAULT FALSE"),
            ("requires_jury_panel", "BOOLEAN DEFAULT FALSE"),
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                await session.execute(text(
                    f"ALTER TABLE competitions ADD COLUMN {column_name} {column_def}"
                ))

        await session.commit()
    except Exception as e:
        print(f"  ⚠️  Migration 003: {e}")
        await session.commit()
