from aiogram.fsm.state import State, StatesGroup

class ContactStates(StatesGroup):
    """Состояния для отправки сообщения команде."""

    waiting_for_message = State()

