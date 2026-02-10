import os
import sys
from pathlib import Path
from django.apps import AppConfig
from django.db import models

class BotDataAppConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel.apps.BotDataApp'
    verbose_name = 'Bot Data Management'

class SQLAlchemyModelProxy:

    def __init__(self):
        self.models = {}

    def register(self, name, sqla_model):
        self.models[name] = sqla_model

BotDataApp = BotDataAppConfig
