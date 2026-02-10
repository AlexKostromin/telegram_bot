"""
Модуль состояний FSM.
"""
from .registration import RegistrationStates
from .contact import ContactStates
from .admin import AdminStates

__all__ = ["RegistrationStates", "ContactStates", "AdminStates"]