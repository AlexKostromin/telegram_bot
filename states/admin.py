from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):

    admin_main_menu = State()

    viewing_applications_list = State()
    viewing_application_detail = State()
    confirming_action = State()

    managing_competition = State()
    editing_role_entry = State()