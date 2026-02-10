"""
Скрипт для инициализации БД с тестовыми данными.
"""
import asyncio
from utils import db_manager
from models import CompetitionModel
import json

async def init_sample_competitions():
    """Добавить примеры соревнований в БД."""
    print("🚀 Инициализирую БД...")
    await db_manager.init_db()
    print("✅ Миграции выполнены успешно!")

    async with db_manager.get_session() as session:
        from sqlalchemy import select

        result = await session.execute(select(CompetitionModel))
        existing_competitions = result.scalars().all()

        if existing_competitions:
            print("⚠️ Соревнования уже добавлены в БД")
            return

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
        print(f"✅ Добавлено {len(competitions)} соревнований в БД")

async def main():
    """Главная функция."""
    print("🚀 Инициализация БД с примерами данных...")
    await init_sample_competitions()
    await db_manager.close_db()
    print("✅ Инициализация завершена!")

if __name__ == "__main__":
    asyncio.run(main())
