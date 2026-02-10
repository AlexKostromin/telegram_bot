"""
Django models for Bot Data Management.
These models use the SQLite database created by the Telegram bot.
"""
import os
import sys
from django.db import models
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

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
    target_type = models.CharField(max_length=50, verbose_name='Тип объекта')
    target_id = models.IntegerField(verbose_name='ID объекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Логирование действий'
        verbose_name_plural = 'Логирование действий'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.target_type}:{self.target_id}"

class MessageTemplate(models.Model):
    """Message template for broadcasts."""

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    subject = models.CharField(max_length=500, verbose_name='Тема письма')
    body_telegram = models.TextField(verbose_name='Текст для Telegram')
    body_email = models.TextField(verbose_name='Текст для Email (HTML)')
    available_variables = models.JSONField(default=dict, verbose_name='Доступные переменные')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_by = models.IntegerField(null=True, blank=True, verbose_name='Создан администратором')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        managed = False
        db_table = 'message_templates'
        verbose_name = 'Шаблон сообщения'
        verbose_name_plural = 'Шаблоны сообщений'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

class Broadcast(models.Model):
    """Broadcast campaign."""

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланирована'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершена'),
        ('failed', 'Ошибка'),
    ]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    template_id = models.IntegerField(verbose_name='Шаблон')
    filters = models.JSONField(default=dict, verbose_name='Фильтры получателей')
    send_telegram = models.BooleanField(default=True, verbose_name='Отправлять в Telegram')
    send_email = models.BooleanField(default=False, verbose_name='Отправлять по Email')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='Запланирована на')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    total_recipients = models.IntegerField(default=0, verbose_name='Всего получателей')
    sent_count = models.IntegerField(default=0, verbose_name='Отправлено')
    failed_count = models.IntegerField(default=0, verbose_name='Ошибок')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начало')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершение')
    created_by = models.IntegerField(verbose_name='Создан администратором')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        managed = False
        db_table = 'broadcasts'
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_progress_percent(self):
        """Get progress percentage."""
        if self.total_recipients == 0:
            return 0
        return int((self.sent_count / self.total_recipients) * 100)

class BroadcastRecipient(models.Model):
    """Broadcast recipient delivery status."""

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('failed', 'Ошибка'),
        ('blocked', 'Заблокировано'),
    ]

    id = models.IntegerField(primary_key=True)
    broadcast_id = models.IntegerField(verbose_name='Рассылка')
    user_id = models.IntegerField(verbose_name='Пользователь')
    telegram_id = models.IntegerField(verbose_name='Telegram ID')
    telegram_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус Telegram'
    )
    telegram_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Отправлено в Telegram')
    telegram_error = models.TextField(blank=True, null=True, verbose_name='Ошибка Telegram')
    telegram_message_id = models.IntegerField(null=True, blank=True, verbose_name='ID сообщения')
    email_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус Email'
    )
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Отправлено Email')
    email_error = models.TextField(blank=True, null=True, verbose_name='Ошибка Email')
    email_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Email адрес')
    rendered_subject = models.CharField(max_length=500, blank=True, null=True, verbose_name='Отрендеренная тема')
    rendered_body = models.TextField(blank=True, null=True, verbose_name='Отрендеренный текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        managed = False
        db_table = 'broadcast_recipients'
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылок'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recipient {self.user_id} - {self.broadcast_id}"

    def is_sent(self):
        """Check if sent to at least one channel."""
        return self.telegram_status == 'sent' or self.email_status == 'sent'
