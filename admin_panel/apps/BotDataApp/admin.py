"""
Django admin configuration for Bot Data Management.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from django.db import connection
import sqlite3
import os

from .models import BotDashboardStat, AdminLog, SQLiteDataHelper
from django.db import models as django_models

class Competition(django_models.Model):
    """Django model for Competition."""
    id = django_models.IntegerField(primary_key=True, verbose_name='ID')
    name = django_models.CharField(max_length=255, verbose_name='Название')
    description = django_models.CharField(max_length=500, null=True, blank=True, verbose_name='Описание')
    competition_type = django_models.CharField(max_length=50, verbose_name='Тип соревнования')
    available_roles = django_models.JSONField(null=True, blank=True, verbose_name='Доступные роли')
    player_entry_open = django_models.BooleanField(default=False, verbose_name='Регистрация для игроков открыта')
    voter_entry_open = django_models.BooleanField(default=False, verbose_name='Регистрация для судей открыта')
    viewer_entry_open = django_models.BooleanField(default=False, verbose_name='Регистрация для зрителей открыта')
    adviser_entry_open = django_models.BooleanField(default=False, verbose_name='Регистрация для советников открыта')
    requires_time_slots = django_models.BooleanField(default=False, verbose_name='Требуются временные слоты')
    requires_jury_panel = django_models.BooleanField(default=False, verbose_name='Требуется судейская коллегия')
    is_active = django_models.BooleanField(default=True, verbose_name='Активно')
    start_date = django_models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    end_date = django_models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    created_at = django_models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = django_models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        managed = False
        db_table = 'competitions'
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'

    def __str__(self):
        return f"{self.name}"

    def registration_count(self):
        """Get count of registrations."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE competition_id = %s",
                [self.id]
            )
            return cursor.fetchone()[0]

    def approved_count(self):
        """Get count of approved registrations."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE competition_id = %s AND status = 'approved'",
                [self.id]
            )
            return cursor.fetchone()[0]

class User(django_models.Model):
    """Django model for User."""
    id = django_models.IntegerField(primary_key=True, verbose_name='ID')
    telegram_id = django_models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    telegram_username = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Telegram имя пользователя')
    first_name = django_models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя')
    last_name = django_models.CharField(max_length=100, null=True, blank=True, verbose_name='Фамилия')
    phone = django_models.CharField(max_length=20, null=True, blank=True, verbose_name='Телефон')
    email = django_models.EmailField(null=True, blank=True, verbose_name='Email')
    country = django_models.CharField(max_length=100, null=True, blank=True, verbose_name='Страна')
    city = django_models.CharField(max_length=100, null=True, blank=True, verbose_name='Город')
    club = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Клуб')
    company = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Компания')
    position = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Должность')
    certificate_name = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Имя для сертификата')
    presentation = django_models.CharField(max_length=500, null=True, blank=True, verbose_name='Представление')
    bio = django_models.TextField(null=True, blank=True, verbose_name='Биография')
    date_of_birth = django_models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    channel_name = django_models.CharField(max_length=255, null=True, blank=True, verbose_name='Имя канала')
    is_active = django_models.BooleanField(default=True, verbose_name='Активен')
    created_at = django_models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = django_models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or f"User #{self.telegram_id}"

    def registration_count(self):
        """Get count of registrations."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE user_id = %s",
                [self.id]
            )
            return cursor.fetchone()[0]

class Registration(django_models.Model):
    """Django model for Registration."""
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    ROLE_CHOICES = [
        ('player', 'Игрок'),
        ('viewer', 'Зритель'),
        ('voter', 'Судья'),
        ('adviser', 'Советник'),
    ]

    id = django_models.IntegerField(primary_key=True, verbose_name='ID')
    user_id = django_models.IntegerField(verbose_name='ID пользователя')
    telegram_id = django_models.BigIntegerField(null=True, blank=True, verbose_name='Telegram ID')
    competition_id = django_models.IntegerField(verbose_name='ID соревнования')
    role = django_models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name='Роль')
    is_confirmed = django_models.BooleanField(default=False, verbose_name='Подтверждено')
    status = django_models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    confirmed_at = django_models.DateTimeField(null=True, blank=True, verbose_name='Подтверждено в')
    confirmed_by = django_models.BigIntegerField(null=True, blank=True, verbose_name='Подтвердил (ID))')
    created_at = django_models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = django_models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        managed = False
        db_table = 'registrations'
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        ordering = ['-id']

    def __str__(self):
        return f"Регистрация #{self.id} ({self.get_status_display()})"

    def get_user(self):
        """Get user object."""
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    def get_competition(self):
        """Get competition object."""
        try:
            return Competition.objects.get(id=self.competition_id)
        except Competition.DoesNotExist:
            return None

class TimeSlot(django_models.Model):
    """Django model for TimeSlot."""
    id = django_models.IntegerField(primary_key=True, verbose_name='ID')
    competition_id = django_models.IntegerField(verbose_name='ID соревнования')
    slot_day = django_models.DateField(verbose_name='День')
    start_time = django_models.TimeField(verbose_name='Начало')
    end_time = django_models.TimeField(verbose_name='Конец')
    max_voters = django_models.IntegerField(default=10, verbose_name='Макс судей')
    is_active = django_models.BooleanField(default=True, verbose_name='Активно')
    created_at = django_models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        managed = False
        db_table = 'time_slots'
        verbose_name = 'Временной слот'
        verbose_name_plural = 'Временные слоты'
        ordering = ['slot_day', 'start_time']

    def __str__(self):
        return f"{self.slot_day} {self.start_time}-{self.end_time}"

    def get_competition(self):
        """Get competition name."""
        try:
            comp = Competition.objects.get(id=self.competition_id)
            return comp.name
        except Competition.DoesNotExist:
            return f"Соревнование #{self.competition_id}"

class JuryPanel(django_models.Model):
    """Django model for JuryPanel."""
    id = django_models.IntegerField(primary_key=True, verbose_name='ID')
    competition_id = django_models.IntegerField(verbose_name='ID соревнования')
    panel_name = django_models.CharField(max_length=100, verbose_name='Название коллегии')
    max_voters = django_models.IntegerField(default=5, verbose_name='Макс судей')
    is_active = django_models.BooleanField(default=True, verbose_name='Активно')
    created_at = django_models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        managed = False
        db_table = 'jury_panels'
        verbose_name = 'Судейская коллегия'
        verbose_name_plural = 'Судейские коллегии'

    def __str__(self):
        return self.panel_name

    def get_competition(self):
        """Get competition name."""
        try:
            comp = Competition.objects.get(id=self.competition_id)
            return comp.name
        except Competition.DoesNotExist:
            return f"Соревнование #{self.competition_id}"

@admin.register(BotDashboardStat)
class BotDashboardStatAdmin(admin.ModelAdmin):
    """Admin interface for Dashboard Statistics."""

    list_display = ['stat_name', 'stat_value', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['stat_name']
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        """Only superusers can add statistics."""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete statistics."""
        return request.user.is_superuser

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin interface for Admin Activity Logs."""

    list_display = ['get_action_badge', 'target_type', 'target_id', 'created_at']
    list_filter = ['action', 'target_type', 'created_at']
    search_fields = ['description', 'target_id']
    readonly_fields = ['admin_id', 'action', 'target_type', 'target_id', 'description', 'created_at']

    def get_action_badge(self, obj):
        """Display action with color badge."""
        colors = {
            'approve': '#28a745',
            'reject': '#dc3545',
            'revoke': '#ffc107',
            'update_competition': '#007bff',
            'delete_user': '#e83e8c',
            'other': '#6c757d',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )

    get_action_badge.short_description = 'Действие'

    def has_add_permission(self, request):
        """Users cannot manually add logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete logs."""
        return request.user.is_superuser

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """Admin interface for Competitions."""

    list_display = ['name', 'competition_type', 'get_status_badge', 'get_registration_count', 'created_at']
    list_filter = ['competition_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_registration_stats']
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'name', 'description', 'competition_type', 'is_active', 'created_at', 'updated_at')
        }),
        ('Доступные роли', {
            'fields': ('player_entry_open', 'voter_entry_open', 'viewer_entry_open', 'adviser_entry_open', 'available_roles'),
            'classes': ('collapse',)
        }),
        ('Параметры', {
            'fields': ('requires_time_slots', 'requires_jury_panel', 'start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('get_registration_stats',)
        }),
    )

    def get_status_badge(self, obj):
        """Display status badge."""
        if obj.is_active:
            color, text = '#28a745', 'Активно'
        else:
            color, text = '#dc3545', 'Неактивно'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 4px;">{}</span>',
            color, text
        )
    get_status_badge.short_description = 'Статус'

    def get_registration_count(self, obj):
        """Get registration count."""
        count = obj.registration_count()
        approved = obj.approved_count()
        return format_html(
            '<span title="Одобрено: {}">Всего: {}</span>',
            approved, count
        )
    get_registration_count.short_description = 'Регистрации'

    def get_registration_stats(self, obj):
        """Get detailed registration statistics."""
        total = obj.registration_count()
        approved = obj.approved_count()
        return format_html(
            '<strong>Всего регистраций:</strong> {}<br/>'
            '<strong>Одобрено:</strong> {}<br/>'
            '<strong>На рассмотрении:</strong> {}',
            total, approved, total - approved
        )
    get_registration_stats.short_description = 'Статистика регистраций'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for Users."""

    list_display = ['get_full_name', 'telegram_id', 'phone', 'email', 'get_registration_count', 'created_at']
    list_filter = ['country', 'city', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'telegram_id', 'email', 'phone', 'telegram_username']
    readonly_fields = ['id', 'telegram_id', 'created_at', 'updated_at']
    actions = ['send_notification_action']
    fieldsets = (
        ('Telegram', {
            'fields': ('id', 'telegram_id', 'telegram_username')
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'date_of_birth')
        }),
        ('Организация', {
            'fields': ('country', 'city', 'club', 'company', 'position')
        }),
        ('Профиль', {
            'fields': ('bio', 'channel_name', 'certificate_name', 'presentation'),
            'classes': ('collapse',)
        }),
        ('Статус и метаданные', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def send_notification_action(self, request, queryset):
        """Send notification to selected users via Telegram and Email."""
        import asyncio
        import os
        import sys
        sys.path.insert(0, '/home/alex/Документы/telegram_bot')

        from aiogram import Bot
        from utils.notifications import notify_user, send_email

        users = list(queryset.values_list('telegram_id', 'email', 'first_name', 'last_name'))
        count = len(users)

        message_tg = """
🔔 ВАЖНОЕ УВЕДОМЛЕНИЕ

Уважаемые участники!

Соревнование начинается завтра!
Не забудьте проверить свои данные в профиле.

Если у вас есть вопросы, свяжитесь с организаторами.

С уважением,
Команда USN
        """.strip()

        message_email = """
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
<p>🔔 <strong>ВАЖНОЕ УВЕДОМЛЕНИЕ</strong></p>

<p>Уважаемые участники!</p>

<p>Соревнование начинается завтра!<br>
Не забудьте проверить свои данные в профиле.</p>

<p>Если у вас есть вопросы, свяжитесь с организаторами.</p>

<p>С уважением,<br>
Команда USN</p>
</body>
</html>
        """.strip()

        from dotenv import load_dotenv
        load_dotenv('/home/alex/Документы/telegram_bot/.env')
        bot_token = os.getenv('BOT_TOKEN')

        if not bot_token:
            self.message_user(request, f'❌ Ошибка: BOT_TOKEN не найден в .env', level='ERROR')
            return

        async def send_all():
            bot = Bot(token=bot_token)
            sent_tg = 0
            sent_email = 0

            for telegram_id, email, first_name, last_name in users:
                user_name = f"{first_name} {last_name}".strip()

                try:
                    await notify_user(
                        bot=bot,
                        telegram_id=telegram_id,
                        message=message_tg
                    )
                    sent_tg += 1
                except Exception as e:
                    print(f"❌ Telegram error for {user_name}: {e}")

                if email:
                    try:
                        await send_email(
                            email_address=email,
                            subject="ВАЖНОЕ УВЕДОМЛЕНИЕ - Соревнование начинается завтра!",
                            body=message_email
                        )
                        sent_email += 1
                    except Exception as e:
                        print(f"❌ Email error for {user_name}: {e}")

            await bot.session.close()
            return sent_tg, sent_email

        try:
            sent_tg, sent_email = asyncio.run(send_all())
            msg = f'✅ Telegram: {sent_tg}/{count} | Email: {sent_email}/{count}'
            self.message_user(request, msg)
        except Exception as e:
            self.message_user(request, f'❌ Ошибка при отправке: {str(e)}', level='ERROR')

    send_notification_action.short_description = '📤 Отправить в Telegram + Email'

    def get_full_name(self, obj):
        """Get full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or f"User #{obj.telegram_id}"
    get_full_name.short_description = 'ФИО'

    def get_registration_count(self, obj):
        """Get registration count."""
        return obj.registration_count()
    get_registration_count.short_description = 'Регистрации'

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete users."""
        return request.user.is_superuser

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Admin interface for Registrations."""

    list_display = ['id', 'get_user_name', 'get_competition_name', 'role', 'get_status_badge', 'created_at']
    list_filter = ['status', 'role', 'is_confirmed', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'competition__name', 'telegram_id']
    readonly_fields = ['id', 'user_id', 'telegram_id', 'competition_id', 'created_at', 'updated_at', 'confirmed_at', 'get_user_info', 'get_competition_info']
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'user_id', 'telegram_id', 'competition_id', 'role', 'status', 'is_confirmed', 'created_at', 'updated_at')
        }),
        ('Подтверждение', {
            'fields': ('confirmed_at', 'confirmed_by'),
            'classes': ('collapse',)
        }),
        ('Сведения о пользователе', {
            'fields': ('get_user_info',),
            'classes': ('wide',)
        }),
        ('Сведения о соревновании', {
            'fields': ('get_competition_info',),
            'classes': ('wide',)
        }),
    )
    actions = ['approve_registrations', 'reject_registrations', 'mark_as_confirmed']

    def get_user_name(self, obj):
        """Get user name."""
        user = obj.get_user()
        if user:
            return f"{user.first_name} {user.last_name}".strip()
        return "N/A"
    get_user_name.short_description = 'Пользователь'

    def get_competition_name(self, obj):
        """Get competition name."""
        competition = obj.get_competition()
        if competition:
            return competition.name
        return "N/A"
    get_competition_name.short_description = 'Соревнование'

    def get_status_badge(self, obj):
        """Display status badge."""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 4px;">{}</span>',
            color, obj.get_status_display()
        )
    get_status_badge.short_description = 'Статус'

    def get_user_info(self, obj):
        """Get detailed user information."""
        user = obj.get_user()
        if user:
            return format_html(
                '<strong>ФИО:</strong> {} {}<br/>'
                '<strong>Telegram ID:</strong> {}<br/>'
                '<strong>Электронная почта:</strong> {}<br/>'
                '<strong>Телефон:</strong> {}<br/>'
                '<strong>Страна/Город:</strong> {}, {}',
                user.first_name, user.last_name,
                user.telegram_id,
                user.email or 'Не указано',
                user.phone or 'Не указано',
                user.country or 'Не указано',
                user.city or 'Не указано'
            )
        return "Пользователь не найден"
    get_user_info.short_description = 'Информация о пользователе'

    def get_competition_info(self, obj):
        """Get detailed competition information."""
        competition = obj.get_competition()
        if competition:
            return format_html(
                '<strong>Название:</strong> {}<br/>'
                '<strong>Тип соревнования:</strong> {}<br/>'
                '<strong>Статус:</strong> {}<br/>'
                '<strong>Создано:</strong> {}',
                competition.name,
                competition.competition_type,
                'Активно' if competition.is_active else 'Неактивно',
                competition.created_at.strftime('%d.%m.%Y %H:%M')
            )
        return "Соревнование не найдено"
    get_competition_info.short_description = 'Информация о соревновании'

    def approve_registrations(self, request, queryset):
        """Bulk approve registrations."""
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'✅ Одобрено {updated} заявок.')
    approve_registrations.short_description = 'Одобрить выбранные заявки'

    def reject_registrations(self, request, queryset):
        """Bulk reject registrations."""
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'❌ Отклонено {updated} заявок.')
    reject_registrations.short_description = 'Отклонить выбранные заявки'

    def mark_as_confirmed(self, request, queryset):
        """Mark registrations as confirmed."""
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f'✔️ Подтверждено {updated} заявок.')
    mark_as_confirmed.short_description = 'Отметить как подтвержденные'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """Admin interface for Time Slots."""

    list_display = ['slot_day', 'start_time', 'end_time', 'get_competition_name', 'max_voters', 'is_active']
    list_filter = ['slot_day', 'is_active', 'competition_id']
    search_fields = ['competition_id']
    readonly_fields = ['created_at', 'get_competition_name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('competition_id', 'get_competition_name', 'slot_day', 'start_time', 'end_time')
        }),
        ('Параметры', {
            'fields': ('max_voters', 'is_active')
        }),
        ('Система', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_competition_name(self, obj):
        """Get competition name."""
        return obj.get_competition()
    get_competition_name.short_description = 'Соревнование'

    def save_model(self, request, obj, form, change):
        """Save model and show message."""
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'✅ Временной слот обновлен: {obj.slot_day} {obj.start_time}-{obj.end_time}')
        else:
            self.message_user(request, f'✅ Временной слот создан: {obj.slot_day} {obj.start_time}-{obj.end_time}')

@admin.register(JuryPanel)
class JuryPanelAdmin(admin.ModelAdmin):
    """Admin interface for Jury Panels."""

    list_display = ['panel_name', 'get_competition_name', 'max_voters', 'is_active']
    list_filter = ['is_active', 'competition_id']
    search_fields = ['panel_name', 'competition_id']
    readonly_fields = ['created_at', 'get_competition_name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('competition_id', 'get_competition_name', 'panel_name')
        }),
        ('Параметры', {
            'fields': ('max_voters', 'is_active')
        }),
        ('Система', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_competition_name(self, obj):
        """Get competition name."""
        return obj.get_competition()
    get_competition_name.short_description = 'Соревнование'

    def save_model(self, request, obj, form, change):
        """Save model and show message."""
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'✅ Судейская коллегия обновлена: {obj.panel_name}')
        else:
            self.message_user(request, f'✅ Судейская коллегия создана: {obj.panel_name}')

class MessageTemplateAdmin(admin.ModelAdmin):
    """Admin interface for message templates."""

    list_display = ('name', 'is_active', 'get_preview', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'available_variables_display')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Содержание', {
            'fields': ('subject', 'body_telegram', 'body_email')
        }),
        ('Переменные', {
            'fields': ('available_variables_display',),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_preview(self, obj):
        """Show template preview in list view."""
        return format_html(
            '<button style="background-color: #417690; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;">'
            'Предпросмотр</button>'
        )
    get_preview.short_description = 'Действие'

    def available_variables_display(self, obj):
        """Display available variables."""
        if not obj.available_variables:
            return "Переменные не определены"
        html = "<table style='width: 100%;'>"
        for var, desc in obj.available_variables.items():
            html += f"<tr><td><code>{var}</code></td><td>{desc}</td></tr>"
        html += "</table>"
        return format_html(html)
    available_variables_display.short_description = 'Доступные переменные'

class BroadcastRecipientInline(admin.TabularInline):
    """Inline view of broadcast recipients."""

    model = __import__('admin_panel.apps.BotDataApp.models', fromlist=['BroadcastRecipient']).BroadcastRecipient
    extra = 0
    readonly_fields = (
        'user_id', 'telegram_id', 'email_address',
        'telegram_status', 'telegram_sent_at', 'email_status', 'email_sent_at'
    )
    can_delete = False
    fields = ('user_id', 'telegram_id', 'email_address', 'telegram_status', 'email_status')

class BroadcastAdmin(admin.ModelAdmin):
    """Admin interface for broadcasts."""

    list_display = (
        'name',
        'get_status_badge',
        'get_progress_bar',
        'get_recipient_count',
        'created_at'
    )
    list_filter = ('status', 'send_telegram', 'send_email', 'created_at')
    search_fields = ('name', 'template_id')
    readonly_fields = (
        'created_at', 'updated_at', 'started_at', 'completed_at',
        'total_recipients', 'sent_count', 'failed_count',
        'get_filter_summary'
    )
    actions = ['execute_broadcast', 'reset_broadcast']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'status', 'template_id')
        }),
        ('Настройки доставки', {
            'fields': ('send_telegram', 'send_email')
        }),
        ('Фильтры получателей', {
            'fields': ('filters', 'get_filter_summary'),
            'classes': ('wide',)
        }),
        ('Статистика', {
            'fields': ('total_recipients', 'sent_count', 'failed_count'),
        }),
        ('Временные метки', {
            'fields': ('scheduled_at', 'started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )

    def get_status_badge(self, obj):
        """Show status as colored badge."""
        status_colors = {
            'draft': '#999',
            'scheduled': '#FF9800',
            'in_progress': '#2196F3',
            'completed': '#4CAF50',
            'failed': '#F44336',
        }
        color = status_colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
            '{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Статус'

    def get_progress_bar(self, obj):
        """Show progress bar."""
        if obj.total_recipients == 0:
            return "Без получателей"
        progress = obj.get_progress_percent()
        return format_html(
            '<div style="width: 200px; height: 20px; background-color: #eee; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: #4CAF50; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;">'
            '{}%</div></div>',
            progress,
            progress
        )
    get_progress_bar.short_description = 'Прогресс'

    def get_recipient_count(self, obj):
        """Show recipient count."""
        return format_html(
            '<strong>{}</strong> / {} ({} ошибок)',
            obj.sent_count,
            obj.total_recipients,
            obj.failed_count
        )
    get_recipient_count.short_description = 'Отправлено'

    def get_filter_summary(self, obj):
        """Show filter summary."""
        if not obj.filters:
            return "Фильтры не установлены"
        html = "<ul>"
        for key, value in obj.filters.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        return format_html(html)
    get_filter_summary.short_description = 'Применяемые фильтры'

    def execute_broadcast(self, request, queryset):
        """Execute selected broadcasts."""
        selected = queryset.filter(status='draft')
        updated = selected.update(status='in_progress')
        self.message_user(request, f'✅ Запущено {updated} рассылок.')
    execute_broadcast.short_description = '▶️ Запустить выбранные рассылки'

    def reset_broadcast(self, request, queryset):
        """Reset broadcast to draft."""
        updated = queryset.update(status='draft', sent_count=0, failed_count=0)
        self.message_user(request, f'🔄 Сброшено {updated} рассылок.')
    reset_broadcast.short_description = '🔄 Сбросить на черновик'

class BroadcastRecipientAdmin(admin.ModelAdmin):
    """Admin interface for broadcast recipients."""

    list_display = (
        'user_id',
        'email_address',
        'get_telegram_status',
        'get_email_status',
        'created_at'
    )
    list_filter = ('telegram_status', 'email_status', 'created_at', 'broadcast_id')
    search_fields = ('user_id', 'email_address', 'telegram_id')
    readonly_fields = (
        'broadcast_id', 'user_id', 'telegram_id', 'email_address',
        'telegram_status', 'telegram_sent_at', 'telegram_error',
        'email_status', 'email_sent_at', 'email_error',
        'rendered_subject', 'rendered_body', 'created_at', 'updated_at'
    )
    can_delete = False

    fieldsets = (
        ('Получатель', {
            'fields': ('broadcast_id', 'user_id', 'telegram_id', 'email_address')
        }),
        ('Доставка в Telegram', {
            'fields': ('telegram_status', 'telegram_sent_at', 'telegram_error', 'telegram_message_id'),
        }),
        ('Доставка по Email', {
            'fields': ('email_status', 'email_sent_at', 'email_error'),
        }),
        ('Отрендеренное содержание', {
            'fields': ('rendered_subject', 'rendered_body'),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_telegram_status(self, obj):
        """Show Telegram status with icon."""
        status_icons = {
            'pending': '⏳',
            'sent': '✅',
            'delivered': '✔️',
            'failed': '❌',
            'blocked': '🚫',
        }
        icon = status_icons.get(obj.telegram_status, '?')
        colors = {
            'pending': '#FF9800',
            'sent': '#4CAF50',
            'failed': '#F44336',
            'blocked': '#9C27B0',
        }
        color = colors.get(obj.telegram_status, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_telegram_status_display() if hasattr(obj, 'get_telegram_status_display') else obj.telegram_status
        )
    get_telegram_status.short_description = 'Telegram'

    def get_email_status(self, obj):
        """Show Email status with icon."""
        status_icons = {
            'pending': '⏳',
            'sent': '✅',
            'delivered': '✔️',
            'failed': '❌',
            'blocked': '🚫',
        }
        icon = status_icons.get(obj.email_status, '?')
        colors = {
            'pending': '#FF9800',
            'sent': '#4CAF50',
            'failed': '#F44336',
            'blocked': '#9C27B0',
        }
        color = colors.get(obj.email_status, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_email_status_display() if hasattr(obj, 'get_email_status_display') else obj.email_status
        )
    get_email_status.short_description = 'Email'

class BotDataAdmin(admin.AdminSite):
    """Custom admin site for Bot Data Management."""

    site_header = "USN Telegram Bot - Администрирование"
    site_title = "Админка бота"
    index_title = "Добро пожаловать в панель администрирования"

    def index(self, request, extra_context=None):
        """Customize admin index page with bot statistics."""
        extra_context = extra_context or {}

        try:
            user_count = SQLiteDataHelper.get_user_count()
            competition_count = SQLiteDataHelper.get_competition_count()
            registration_count = SQLiteDataHelper.get_registration_count()
            reg_by_status = SQLiteDataHelper.get_registrations_by_status()
            recent_registrations = SQLiteDataHelper.get_recent_registrations(5)
            users_by_role = SQLiteDataHelper.get_users_by_role()

            extra_context.update({
                'user_count': user_count,
                'competition_count': competition_count,
                'registration_count': registration_count,
                'reg_by_status': reg_by_status,
                'recent_registrations': recent_registrations,
                'users_by_role': users_by_role,
                'show_bot_stats': True,
            })
        except Exception as e:
            extra_context['bot_stats_error'] = str(e)

        return super().index(request, extra_context)

bot_admin_site = BotDataAdmin(name='bot_admin')

bot_admin_site.register(BotDashboardStat, BotDashboardStatAdmin)
bot_admin_site.register(AdminLog, AdminLogAdmin)

bot_admin_site.register(Competition, CompetitionAdmin)
bot_admin_site.register(User, UserAdmin)
bot_admin_site.register(Registration, RegistrationAdmin)
bot_admin_site.register(TimeSlot, TimeSlotAdmin)
bot_admin_site.register(JuryPanel, JuryPanelAdmin)

from .models import MessageTemplate, Broadcast, BroadcastRecipient
bot_admin_site.register(MessageTemplate, MessageTemplateAdmin)
bot_admin_site.register(Broadcast, BroadcastAdmin)
bot_admin_site.register(BroadcastRecipient, BroadcastRecipientAdmin)
