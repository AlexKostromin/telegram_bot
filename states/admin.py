"""
FSM states for admin panel.
"""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """States for admin panel."""

    # Main menu
    admin_main_menu = State()

    # Application management
    viewing_applications_list = State()
    viewing_application_detail = State()
    confirming_action = State()

    # Competition management
    managing_competition = State()
    editing_role_entry = State()

    # Time slot management
    managing_time_slots = State()
    creating_time_slot = State()
    waiting_for_slot_day = State()
    waiting_for_slot_start = State()
    waiting_for_slot_end = State()
    waiting_for_slot_max_voters = State()

    # Jury panel management
    managing_jury_panels = State()
    creating_jury_panel = State()
    waiting_for_panel_name = State()
    waiting_for_panel_max_voters = State()
