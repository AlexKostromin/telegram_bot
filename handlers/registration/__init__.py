from .competition_select import competition_select_router
from .role_select import role_select_router
from .user_create import user_create_router
from .user_edit import user_edit_router
from .voter_slots import voter_slots_router
from .confirmation import confirmation_router

__all__ = [
    "competition_select_router",
    "role_select_router",
    "user_create_router",
    "user_edit_router",
    "voter_slots_router",
    "confirmation_router",
]
