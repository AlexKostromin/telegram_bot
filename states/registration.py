from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):

    waiting_for_competition_select = State()

    waiting_for_role_select = State()

    waiting_for_existing_user_confirmation = State()
    waiting_for_edit_field_select = State()
    waiting_for_field_edit_input = State()
    waiting_for_edit_confirmation = State()

    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_country = State()
    waiting_for_city = State()
    waiting_for_club = State()
    waiting_for_role_confirmation_first = State()
    waiting_for_certificate_name = State()
    waiting_for_company = State()
    waiting_for_position = State()
    waiting_for_role_confirmation_repeat = State()
    waiting_for_presentation = State()

    waiting_for_time_slot_selection = State()
    waiting_for_jury_panel_selection = State()

    waiting_for_final_confirmation = State()

    registration_complete = State()
