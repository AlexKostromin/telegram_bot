from functools import wraps
from typing import Callable, Union, Any
from config import ADMIN_IDS
from aiogram.types import CallbackQuery, Message
from messages.texts import BotMessages

def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS

def admin_only(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict access to admins only."""
    @wraps(handler)
    async def wrapper(event: Union[CallbackQuery, Message], *args: Any, **kwargs: Any) -> Any:
        user_id: int = event.from_user.id
        if not is_admin(user_id):
            if isinstance(event, CallbackQuery):
                await event.answer("⛔ Доступ запрещен", show_alert=True)
            else:
                await event.answer("⛔ Доступ запрещен")
            return
        return await handler(event, *args, **kwargs)
    return wrapper

