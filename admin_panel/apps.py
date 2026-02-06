"""
Django app configuration for bot data management.
"""
import os
import sys
from pathlib import Path
from django.apps import AppConfig
from django.db import models


class BotDataAppConfig(AppConfig):
    """Configuration for the bot data management app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel.apps.BotDataApp'
    verbose_name = 'Bot Data Management'


# Create a compatibility layer to use SQLAlchemy models with Django Admin
class SQLAlchemyModelProxy:
    """Proxy to make SQLAlchemy models available in Django Admin."""

    def __init__(self):
        self.models = {}

    def register(self, name, sqla_model):
        """Register a SQLAlchemy model."""
        self.models[name] = sqla_model


# Alias for easier import
BotDataApp = BotDataAppConfig