"""
Migration 001: Rename roles from spectator→viewer and second→adviser.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import json


async def migrate(session: AsyncSession):
    """
    Rename roles in registrations and competitions.
    - registrations.role: 'spectator' -> 'viewer', 'second' -> 'adviser'
    - competitions.available_roles: update JSON array

    This migration is safe on fresh installs (tables don't exist yet).
    """
    try:
        # Update registrations table (may not exist on fresh install)
        try:
            await session.execute(text("""
                UPDATE registrations SET role = 'viewer' WHERE role = 'spectator'
            """))

            await session.execute(text("""
                UPDATE registrations SET role = 'adviser' WHERE role = 'second'
            """))
        except Exception:
            # Table doesn't exist yet (fresh install), skip
            pass

        # Update competitions table (may not exist on fresh install)
        try:
            result = await session.execute(text("""
                SELECT id, available_roles FROM competitions
            """))

            competitions = result.fetchall()

            for comp_id, available_roles_json in competitions:
                if available_roles_json is None:
                    continue

                try:
                    # Parse JSON
                    if isinstance(available_roles_json, str):
                        available_roles = json.loads(available_roles_json)
                    else:
                        available_roles = available_roles_json

                    # Replace role names
                    updated_roles = []
                    for role in available_roles:
                        if role == 'spectator':
                            updated_roles.append('viewer')
                        elif role == 'second':
                            updated_roles.append('adviser')
                        else:
                            updated_roles.append(role)

                    # Update in DB
                    await session.execute(text("""
                        UPDATE competitions SET available_roles = :roles WHERE id = :id
                    """), {
                        "roles": json.dumps(updated_roles),
                        "id": comp_id
                    })
                except Exception as e:
                    print(f"Warning: Could not update competition {comp_id}: {e}")
        except Exception:
            # Table doesn't exist yet (fresh install), skip
            pass

        await session.commit()

    except Exception as e:
        print(f"  ⚠️  Migration 001 skipped (fresh install): {e}")
        await session.commit()
