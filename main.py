"""
Точка входа для запуска Telegram бота USN.
"""
import asyncio
import logging
from typing import Optional
from bot import USNBot
from utils import db_manager
from config import LOGGING_LEVEL
from models import CompetitionModel
import json
from sqlalchemy import select

logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def init_sample_data() -> None:
    """Добавить примеры соревнований в БД если их еще нет."""
    logger.info("=== STARTING init_sample_data ===")
    try:
        async with db_manager.get_session() as session:
            result = await session.execute(select(CompetitionModel))
            existing_competitions = result.scalars().all()
            logger.info(f"Found {len(existing_competitions)} existing competitions")

            if existing_competitions:
                logger.info("Competitions already exist, skipping sample data")
                return

            logger.info("Adding sample competitions...")
            competitions = [
            CompetitionModel(
                name="Чемпионат USN 2024",
                description="Основной чемпионат сезона 2024",
                competition_type="classic_game",
                available_roles=json.dumps(["player", "adviser", "viewer", "voter"]),
                player_entry_open=True,
                voter_entry_open=True,
                viewer_entry_open=True,
                adviser_entry_open=True,
                requires_time_slots=False,
                requires_jury_panel=False,
                is_active=True,
            ),
            CompetitionModel(
                name="Квалификационный турнир",
                description="Турнир для отбора участников",
                competition_type="tournament",
                available_roles=json.dumps(["player", "viewer", "voter"]),
                player_entry_open=True,
                voter_entry_open=True,
                viewer_entry_open=True,
                adviser_entry_open=False,
                requires_time_slots=False,
                requires_jury_panel=False,
                is_active=True,
            ),
            CompetitionModel(
                name="Онлайн чемпионат",
                description="Онлайн формат соревнований",
                competition_type="online",
                available_roles=json.dumps(["player", "viewer", "voter"]),
                player_entry_open=True,
                voter_entry_open=True,
                viewer_entry_open=True,
                adviser_entry_open=False,
                requires_time_slots=False,
                requires_jury_panel=False,
                is_active=True,
            ),
        ]

        for comp in competitions:
            session.add(comp)

        await session.commit()
        logger.info(f"Added {len(competitions)} competitions to DB")
    except Exception as e:
        logger.error(f"Error in init_sample_data: {e}", exc_info=True)

async def main() -> None:
    """Главная функция для запуска бота."""
    logger.info("Инициализация Telegram бота USN...")

    try:

        await db_manager.init_db()
        logger.info("База данных инициализирована")

        logger.info("BEFORE init_sample_data")
        await init_sample_data()
        logger.info("AFTER init_sample_data")
    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        raise

    bot: USNBot = USNBot()
    logger.info("Бот инициализирован")

    try:
        logger.info("Запуск polling...")
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}", exc_info=True)
    finally:
        await db_manager.close_db()
        await bot.close()
        logger.info("Бот выключен")

if __name__ == "__main__":
    asyncio.run(main())
