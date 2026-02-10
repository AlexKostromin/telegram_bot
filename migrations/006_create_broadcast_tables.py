"""
Migration 006: Create broadcast system tables.
Creates message_templates, broadcasts, and broadcast_recipients tables.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


async def migrate(session: AsyncSession):
    """
    Create broadcast system tables (database-agnostic):
    - message_templates: Шаблоны сообщений
    - broadcasts: Рассылки
    - broadcast_recipients: Результаты доставки

    This migration is safe on fresh installs (creates tables if not exist).
    """
    pk = "SERIAL PRIMARY KEY"
    bool_true = "TRUE"
    bool_false = "FALSE"
    ts = "TIMESTAMP"
    now = "CURRENT_TIMESTAMP"

    try:
        # Create message_templates
        await session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS message_templates (
                id {pk},
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                subject VARCHAR(500) NOT NULL,
                body_telegram TEXT NOT NULL,
                body_email TEXT NOT NULL,
                available_variables JSON NOT NULL DEFAULT '{{}}',
                is_active BOOLEAN DEFAULT {bool_true},
                created_by INTEGER,
                created_at {ts} DEFAULT {now},
                updated_at {ts} DEFAULT {now}
            )
        """))
        logger.info("✅ Created message_templates table")

        # Create message_templates indexes
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_templates_name
            ON message_templates(name)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_templates_is_active
            ON message_templates(is_active)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_templates_created_at
            ON message_templates(created_at)
        """))

        # Create broadcasts
        await session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id {pk},
                name VARCHAR(255) NOT NULL,
                template_id INTEGER NOT NULL,
                filters JSON NOT NULL DEFAULT '{{}}',
                send_telegram BOOLEAN DEFAULT {bool_true},
                send_email BOOLEAN DEFAULT {bool_false},
                scheduled_at {ts},
                status VARCHAR(20) DEFAULT 'draft',
                total_recipients INTEGER DEFAULT 0,
                sent_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                started_at {ts},
                completed_at {ts},
                created_by INTEGER NOT NULL,
                created_at {ts} DEFAULT {now},
                updated_at {ts} DEFAULT {now},
                FOREIGN KEY (template_id) REFERENCES message_templates(id)
            )
        """))
        logger.info("✅ Created broadcasts table")

        # Create broadcasts indexes
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcasts_name
            ON broadcasts(name)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcasts_template_id
            ON broadcasts(template_id)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcasts_status
            ON broadcasts(status)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcasts_created_at
            ON broadcasts(created_at)
        """))

        # Create broadcast_recipients
        await session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS broadcast_recipients (
                id {pk},
                broadcast_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                telegram_id BIGINT NOT NULL,
                telegram_status VARCHAR(20) DEFAULT 'pending',
                telegram_sent_at {ts},
                telegram_error TEXT,
                telegram_message_id INTEGER,
                email_status VARCHAR(20) DEFAULT 'pending',
                email_sent_at {ts},
                email_error TEXT,
                email_address VARCHAR(255),
                rendered_subject VARCHAR(500),
                rendered_body TEXT,
                created_at {ts} DEFAULT {now},
                updated_at {ts} DEFAULT {now},
                FOREIGN KEY (broadcast_id) REFERENCES broadcasts(id)
            )
        """))
        logger.info("✅ Created broadcast_recipients table")

        # Create broadcast_recipients indexes
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_broadcast_id
            ON broadcast_recipients(broadcast_id)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_user_id
            ON broadcast_recipients(user_id)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_telegram_id
            ON broadcast_recipients(telegram_id)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_telegram_status
            ON broadcast_recipients(telegram_status)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_email_status
            ON broadcast_recipients(email_status)
        """))

        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_created_at
            ON broadcast_recipients(created_at)
        """))

        await session.commit()
        logger.info("✅ Migration 006 completed: Broadcast tables created successfully")

    except Exception as e:
        logger.error(f"❌ Migration 006 failed: {e}")
        await session.rollback()
        raise
