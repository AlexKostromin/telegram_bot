"""
Django models for Bot Data Management.
These models use the SQLite database created by the Telegram bot.
"""
import os
import sys
from django.db import models
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from models.user import User
    from models.competition import Competition
    from models.registration import Registration
    from models.time_slot import TimeSlot
    from models.voter_time_slot import VoterTimeSlot
    from models.jury_panel import JuryPanel
    from models.voter_jury_panel import VoterJuryPanel
    SQLALCHEMY_MODELS_AVAILABLE = True
except ImportError:
    SQLALCHEMY_MODELS_AVAILABLE = False


class BotDashboardStat(models.Model):
    """Cache statistics for the dashboard."""

    stat_name = models.CharField(max_length=100, unique=True, verbose_name='Название статистики')
    stat_value = models.IntegerField(default=0, verbose_name='Значение')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        return f"{self.stat_name}: {self.stat_value}"


class SQLiteDataHelper(models.Model):
    """Helper model to access raw SQLite data."""

    class Meta:
        managed = False
        abstract = True

    @staticmethod
    def execute_raw_query(query, params=None):
        """Execute raw SQL query and return results."""
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_user_count():
        """Get total number of users."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT COUNT(*) as count FROM users"
            )
            return results[0]['count'] if results else 0
        except Exception:
            return 0

    @staticmethod
    def get_competition_count():
        """Get total number of competitions."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT COUNT(*) as count FROM competitions"
            )
            return results[0]['count'] if results else 0
        except Exception:
            return 0

    @staticmethod
    def get_registration_count():
        """Get total number of registrations."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT COUNT(*) as count FROM registrations"
            )
            return results[0]['count'] if results else 0
        except Exception:
            return 0

    @staticmethod
    def get_registrations_by_status():
        """Get registration count by status."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT status, COUNT(*) as count FROM registrations GROUP BY status"
            )
            return results
        except Exception:
            return []

    @staticmethod
    def get_active_competitions():
        """Get list of active competitions."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT id, name FROM competitions WHERE is_active = 1"
            )
            return results
        except Exception:
            return []

    @staticmethod
    def get_recent_registrations(limit=10):
        """Get recent registrations."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                f"""
                SELECT r.id, r.user_id, r.competition_id, r.role, r.status,
                       u.first_name, u.last_name, c.name as competition_name
                FROM registrations r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN competitions c ON r.competition_id = c.id
                ORDER BY r.id DESC
                LIMIT {limit}
                """
            )
            return results
        except Exception:
            return []

    @staticmethod
    def get_users_by_role():
        """Get user count by role in registrations."""
        try:
            results = SQLiteDataHelper.execute_raw_query(
                "SELECT role, COUNT(*) as count FROM registrations GROUP BY role"
            )
            return results
        except Exception:
            return []


class AdminLog(models.Model):
    """Log of admin actions."""

    ACTION_CHOICES = [
        ('approve', 'Одобрена регистрация'),
        ('reject', 'Отклонена регистрация'),
        ('revoke', 'Отозвана регистрация'),
        ('update_competition', 'Обновлено соревнование'),
        ('delete_user', 'Удален пользователь'),
        ('other', 'Другое'),
    ]

    admin_id = models.BigIntegerField(verbose_name='ID администратора')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Действие')
    target_type = models.CharField(max_length=50, verbose_name='Тип объекта')  # 'user', 'registration', 'competition', etc.
    target_id = models.IntegerField(verbose_name='ID объекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Логирование действий'
        verbose_name_plural = 'Логирование действий'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.target_type}:{self.target_id}"