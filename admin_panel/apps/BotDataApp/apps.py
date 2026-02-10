"""
App configuration for Bot Data Management.
"""
from django.apps import AppConfig

class BotDataAppConfig(AppConfig):
    """Bot Data App configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel.apps.BotDataApp'
    verbose_name = 'Bot Data Management'
