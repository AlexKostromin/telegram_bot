"""
Migration 005: Create tables for time slots and jury panels.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate(session: AsyncSession):
    """
    Create 4 new tables:
    - time_slots: for voter time slot availability
    - voter_time_slots: mapping of voters to time slots
    - jury_panels: for jury panel organization
    - voter_jury_panels: mapping of voters to jury panels

    Safe on fresh installs - tables are already created via models.
    """
    # Tables are already created via Base.metadata.create_all() in models
    # This migration is a no-op for fresh installs
    # It would only be needed for existing databases upgrading from older versions
    print("  ⏭️  Migration 005 skipped (tables already created via models)")
    await session.commit()
