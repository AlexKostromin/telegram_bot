from typing import List
from aiogram import Dispatcher, Bot, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import (
    start_router,
    menu_router,
    contact_router,
    competition_select_router,
    role_select_router,
    user_create_router,
    user_edit_router,
    voter_slots_router,
    confirmation_router,
    admin_main_router,
    admin_applications_router,
    admin_competitions_router,
)

class USNBot:

    def __init__(self) -> None:
        self.bot: Bot = Bot(token=BOT_TOKEN)
        self.storage: MemoryStorage = MemoryStorage()
        self.dispatcher: Dispatcher = Dispatcher(storage=self.storage)
        self.default_commands: List[BotCommand] = []
        self._register_handlers()
        self._set_default_commands()

    def _register_handlers(self) -> None:
        self.dispatcher.include_routers(
            admin_main_router,
            admin_applications_router,
            admin_competitions_router,
            start_router,
            menu_router,
            contact_router,
            competition_select_router,
            role_select_router,
            voter_slots_router,
            user_edit_router,
            user_create_router,
            confirmation_router,
        )

    def _set_default_commands(self) -> None:
        self.default_commands = [
            BotCommand(command="start", description="Начать работу с ботом"),
            BotCommand(command="help", description="Справка по использованию"),
            BotCommand(command="admin", description="Админ-панель (только для админов)"),
        ]

    async def set_commands(self) -> None:
        await self.bot.set_my_commands(self.default_commands)

    async def start_polling(self) -> None:
        await self.set_commands()
        try:
            await self.dispatcher.start_polling(self.bot)
        finally:
            await self.bot.session.close()

    async def close(self) -> None:
        await self.bot.session.close()

    def get_dispatcher(self) -> Dispatcher:
        return self.dispatcher

    def get_bot(self) -> Bot:
        return self.bot
