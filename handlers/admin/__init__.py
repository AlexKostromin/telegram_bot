from .main_menu import admin_main_router
from .applications import admin_applications_router
from .competitions import admin_competitions_router

__all__ = [
    "admin_main_router",
    "admin_applications_router",
    "admin_competitions_router",
]

