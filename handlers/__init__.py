"""
Модуль обработчиков бота.
"""
from .start import start_router
from .menu import menu_router
from .contact import contact_router
from .registration import (
    competition_select_router,
    role_select_router,
    user_create_router,
    user_edit_router,
    voter_slots_router,
    confirmation_router,
)
from .admin import (
    admin_main_router,
    admin_applications_router,
    admin_competitions_router,
)

__all__ = [
    "start_router",
    "menu_router",
    "contact_router",
    "competition_select_router",
    "role_select_router",
    "user_create_router",
    "user_edit_router",
    "voter_slots_router",
    "confirmation_router",
    "admin_main_router",
    "admin_applications_router",
    "admin_competitions_router",
]