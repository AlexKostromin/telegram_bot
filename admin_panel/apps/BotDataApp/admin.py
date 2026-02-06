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


# ============ Bot Models (Django wrappers for SQLite tables) ============

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


# ============ Bot Data Admin Classes ============

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


class BotDataAdmin(admin.AdminSite):
    """Custom admin site for Bot Data Management."""

    site_header = "USN Telegram Bot - Администрирование"
    site_title = "Админка бота"
    index_title = "Добро пожаловать в панель администрирования"

    def index(self, request, extra_context=None):
        """Customize admin index page with bot statistics."""
        extra_context = extra_context or {}

        # Get statistics from SQLite database
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


# Create custom admin site instance
bot_admin_site = BotDataAdmin(name='bot_admin')

# Register models with custom admin site
bot_admin_site.register(BotDashboardStat, BotDashboardStatAdmin)
bot_admin_site.register(AdminLog, AdminLogAdmin)
