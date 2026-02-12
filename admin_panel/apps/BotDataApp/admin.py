from django.contrib import admin
from django.utils.html import format_html
from django.db import connection
from django.template.response import TemplateResponse

from .models import BotDashboardStat, AdminLog
from django.db import models as django_models

class Competition(django_models.Model):
    id = django_models.AutoField(primary_key=True, verbose_name='ID')
    name = django_models.CharField(max_length=255, verbose_name='Название')
    description = django_models.CharField(max_length=500, null=True, blank=True, verbose_name='Описание')
    COMPETITION_TYPE_CHOICES = [
        ('classic_game', 'Классическая игра'),
        ('tournament', 'Турнир'),
        ('online', 'Онлайн'),
    ]
    competition_type = django_models.CharField(max_length=50, choices=COMPETITION_TYPE_CHOICES, verbose_name='Тип соревнования')
    available_roles = django_models.JSONField(null=True, blank=True, verbose_name='Доступные роли')
    player_entry_open = django_models.BooleanField(default=True, verbose_name='Регистрация для игроков открыта')
    voter_entry_open = django_models.BooleanField(default=True, verbose_name='Регистрация для судей открыта')
    viewer_entry_open = django_models.BooleanField(default=True, verbose_name='Регистрация для зрителей открыта')
    adviser_entry_open = django_models.BooleanField(default=True, verbose_name='Регистрация для советников открыта')
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
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE competition_id = %s",
                [self.id]
            )
            return cursor.fetchone()[0]

    def approved_count(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE competition_id = %s AND status = 'approved'",
                [self.id]
            )
            return cursor.fetchone()[0]

class User(django_models.Model):
    id = django_models.AutoField(primary_key=True, verbose_name='ID')
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
    classic_rating = django_models.IntegerField(null=True, blank=True, verbose_name='Рейтинг Classic')
    quick_rating = django_models.IntegerField(null=True, blank=True, verbose_name='Рейтинг Quick')
    team_rating = django_models.IntegerField(null=True, blank=True, verbose_name='Рейтинг Team')
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
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE user_id = %s",
                [self.id]
            )
            return cursor.fetchone()[0]

class Registration(django_models.Model):
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

    id = django_models.AutoField(primary_key=True, verbose_name='ID')
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
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    def get_competition(self):
        try:
            return Competition.objects.get(id=self.competition_id)
        except Competition.DoesNotExist:
            return None

class TimeSlot(django_models.Model):
    id = django_models.AutoField(primary_key=True, verbose_name='ID')
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
        try:
            comp = Competition.objects.get(id=self.competition_id)
            return comp.name
        except Competition.DoesNotExist:
            return f"Соревнование #{self.competition_id}"

class JuryPanel(django_models.Model):
    id = django_models.AutoField(primary_key=True, verbose_name='ID')
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
        try:
            comp = Competition.objects.get(id=self.competition_id)
            return comp.name
        except Competition.DoesNotExist:
            return f"Соревнование #{self.competition_id}"

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):

    list_display = ['name', 'competition_type', 'get_status_badge', 'get_registration_count', 'created_at']
    list_filter = ['competition_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_registration_stats',
                       'get_players_list', 'get_voters_list', 'get_viewers_list', 'get_advisers_list']
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'name', 'description', 'competition_type', 'is_active', 'created_at', 'updated_at')
        }),
        ('Entry is Open — регистрация открыта', {
            'fields': ('player_entry_open', 'voter_entry_open', 'viewer_entry_open', 'adviser_entry_open'),
        }),
        ('Параметры', {
            'fields': ('requires_time_slots', 'requires_jury_panel', 'start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('get_registration_stats',)
        }),
        ('Players — Игроки', {
            'fields': ('get_players_list',),
        }),
        ('Voters — Судьи', {
            'fields': ('get_voters_list',),
        }),
        ('Viewers — Зрители', {
            'fields': ('get_viewers_list',),
        }),
        ('Advisers — Советники', {
            'fields': ('get_advisers_list',),
        }),
    )

    def save_model(self, request, obj, form, change):
        import json
        roles = []
        if obj.player_entry_open:
            roles.append("player")
        if obj.voter_entry_open:
            roles.append("voter")
        if obj.viewer_entry_open:
            roles.append("viewer")
        if obj.adviser_entry_open:
            roles.append("adviser")
        obj.available_roles = json.dumps(roles)
        super().save_model(request, obj, form, change)

    def get_status_badge(self, obj):
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
        count = obj.registration_count()
        approved = obj.approved_count()
        return format_html(
            '<span title="Одобрено: {}">Всего: {}</span>',
            approved, count
        )
    get_registration_count.short_description = 'Регистрации'

    def get_registration_stats(self, obj):
        total = obj.registration_count()
        approved = obj.approved_count()
        return format_html(
            '<strong>Всего регистраций:</strong> {}<br/>'
            '<strong>Одобрено:</strong> {}<br/>'
            '<strong>На рассмотрении:</strong> {}',
            total, approved, total - approved
        )
    get_registration_stats.short_description = 'Статистика регистраций'

    def _get_participants_by_role(self, obj, role):
        if not obj.pk:
            return format_html('<em>Сначала сохраните соревнование</em>')
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT u.first_name, u.last_name, u.telegram_username, u.telegram_id, r.status "
                "FROM registrations r JOIN users u ON r.user_id = u.id "
                "WHERE r.competition_id = %s AND r.role = %s ORDER BY r.created_at",
                [obj.id, role]
            )
            rows = cursor.fetchall()
        if not rows:
            return format_html('<em>Нет участников</em>')
        status_colors = {'approved': '#28a745', 'pending': '#ffc107', 'rejected': '#dc3545'}
        status_labels = {'approved': 'Одобрен', 'pending': 'Ожидает', 'rejected': 'Отклонён'}
        html = '<table style="border-collapse:collapse;width:100%">'
        html += '<tr style="background:#f0f0f0"><th style="padding:6px;text-align:left">Имя</th>'
        html += '<th style="padding:6px;text-align:left">Telegram</th>'
        html += '<th style="padding:6px;text-align:left">Статус</th></tr>'
        for first_name, last_name, username, tg_id, status in rows:
            name = f"{first_name or ''} {last_name or ''}".strip() or f"ID {tg_id}"
            tg = f"@{username}" if username else str(tg_id)
            color = status_colors.get(status, '#999')
            label = status_labels.get(status, status)
            html += (
                f'<tr><td style="padding:4px 6px">{name}</td>'
                f'<td style="padding:4px 6px">{tg}</td>'
                f'<td style="padding:4px 6px"><span style="background:{color};color:white;'
                f'padding:2px 8px;border-radius:3px;font-size:11px">{label}</span></td></tr>'
            )
        html += '</table>'
        return format_html(html)

    def get_players_list(self, obj):
        return self._get_participants_by_role(obj, 'player')
    get_players_list.short_description = 'Список игроков'

    def get_voters_list(self, obj):
        return self._get_participants_by_role(obj, 'voter')
    get_voters_list.short_description = 'Список судей'

    def get_viewers_list(self, obj):
        return self._get_participants_by_role(obj, 'viewer')
    get_viewers_list.short_description = 'Список зрителей'

    def get_advisers_list(self, obj):
        return self._get_participants_by_role(obj, 'adviser')
    get_advisers_list.short_description = 'Список советников'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ['get_full_name', 'telegram_id', 'phone', 'email', 'get_registration_count', 'created_at']
    list_filter = ['country', 'city', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'telegram_id', 'email', 'phone', 'telegram_username']
    readonly_fields = ['id', 'telegram_id', 'created_at', 'updated_at']
    actions = ['send_custom_message']
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
        ('Рейтинги (только для игроков)', {
            'fields': ('classic_rating', 'quick_rating', 'team_rating'),
            'classes': ('collapse',)
        }),
        ('Статус и метаданные', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def send_custom_message(self, request, queryset):
        if 'confirm_send' in request.POST:
            message_text = request.POST.get('message', '').strip()
            subject = request.POST.get('subject', '').strip()
            send_telegram = request.POST.get('send_telegram') == '1'
            send_email = request.POST.get('send_email') == '1'

            errors_list = []
            if not message_text:
                errors_list.append('Введите текст сообщения.')
            if not send_telegram and not send_email:
                errors_list.append('Выберите хотя бы один канал доставки.')

            if errors_list:
                recipients = list(queryset)
                return TemplateResponse(request, 'admin/BotDataApp/send_broadcast.html', {
                    **self.admin_site.each_context(request),
                    'title': 'Отправить сообщение',
                    'recipients': recipients,
                    'message': message_text,
                    'subject': subject,
                    'send_telegram': send_telegram,
                    'send_email': send_email,
                    'errors': errors_list,
                    'opts': self.model._meta,
                })

            return self._execute_broadcast(
                request, queryset, message_text, subject, send_telegram, send_email,
            )

        recipients = list(queryset)
        return TemplateResponse(request, 'admin/BotDataApp/send_broadcast.html', {
            **self.admin_site.each_context(request),
            'title': 'Отправить сообщение',
            'recipients': recipients,
            'message': '',
            'subject': '',
            'send_telegram': True,
            'send_email': True,
            'errors': [],
            'opts': self.model._meta,
        })

    send_custom_message.short_description = '📤 Отправить сообщение'

    def _execute_broadcast(self, request, queryset, message_text, subject, send_telegram, send_email):
        import os
        import json
        import logging
        import smtplib
        import urllib.request
        from email.mime.text import MIMEText

        from dotenv import load_dotenv
        load_dotenv()

        logger = logging.getLogger(__name__)

        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token and send_telegram:
            self.message_user(request, 'BOT_TOKEN не найден в .env', level='ERROR')
            return

        smtp_host = os.getenv('SMTP_HOST', '')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        smtp_use_tls = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
        support_email = os.getenv('SUPPORT_EMAIL', '')
        email_from_name = os.getenv('EMAIL_FROM_NAME', 'USN Competitions')
        smtp_configured = all([smtp_host, smtp_username, smtp_password, support_email])

        users = list(queryset.values_list('telegram_id', 'email', 'first_name', 'last_name'))
        count = len(users)
        sent_tg = 0
        sent_email_count = 0
        errors = []

        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        for telegram_id, email, first_name, last_name in users:
            first_name = first_name or ''
            last_name = last_name or ''
            full_name = f"{first_name} {last_name}".strip()

            rendered = message_text.replace('{first_name}', first_name)
            rendered = rendered.replace('{last_name}', last_name)
            rendered = rendered.replace('{full_name}', full_name)

            if send_telegram:
                try:
                    payload = json.dumps({'chat_id': telegram_id, 'text': rendered}).encode('utf-8')
                    req = urllib.request.Request(
                        telegram_api_url,
                        data=payload,
                        headers={'Content-Type': 'application/json'},
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        result = json.loads(resp.read())
                        if result.get('ok'):
                            sent_tg += 1
                        else:
                            errors.append(f"TG {full_name}: {result.get('description', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Telegram error for {full_name}: {e}")
                    errors.append(f"TG {full_name}: {e}")

            if send_email and email and smtp_configured:
                try:
                    rendered_subject = subject or 'Уведомление от USN Competitions'
                    rendered_subject = rendered_subject.replace('{first_name}', first_name)
                    rendered_subject = rendered_subject.replace('{last_name}', last_name)
                    rendered_subject = rendered_subject.replace('{full_name}', full_name)

                    msg = MIMEText(rendered, 'plain', 'utf-8')
                    msg['Subject'] = rendered_subject
                    msg['From'] = f"{email_from_name} <{support_email}>"
                    msg['To'] = email

                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                    if smtp_use_tls:
                        server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
                    server.quit()
                    sent_email_count += 1
                except Exception as e:
                    logger.error(f"Email error for {full_name}: {e}")
                    errors.append(f"Email {full_name}: {e}")

        parts = []
        if send_telegram:
            parts.append(f'Telegram: {sent_tg}/{count}')
        if send_email:
            parts.append(f'Email: {sent_email_count}/{count}')
        result_msg = ' | '.join(parts)
        if errors:
            result_msg += f' | Ошибки: {len(errors)}'
        self.message_user(request, result_msg)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or f"User #{obj.telegram_id}"
    get_full_name.short_description = 'ФИО'

    def get_registration_count(self, obj):
        return obj.registration_count()
    get_registration_count.short_description = 'Регистрации'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

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
    actions = ['approve_registrations', 'reject_registrations', 'revoke_registrations', 'mark_as_confirmed']

    def get_user_name(self, obj):
        user = obj.get_user()
        if user:
            return f"{user.first_name} {user.last_name}".strip()
        return "N/A"
    get_user_name.short_description = 'Пользователь'

    def get_competition_name(self, obj):
        competition = obj.get_competition()
        if competition:
            return competition.name
        return "N/A"
    get_competition_name.short_description = 'Соревнование'

    def get_status_badge(self, obj):
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

    def _notify_users(self, registrations, message_template):
        import os
        import json
        import logging
        import urllib.request
        from dotenv import load_dotenv
        load_dotenv()

        logger = logging.getLogger(__name__)
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            return

        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        for reg in registrations:
            telegram_id = reg.telegram_id
            if not telegram_id:
                user = reg.get_user()
                if user:
                    telegram_id = user.telegram_id
            if not telegram_id:
                continue

            comp = reg.get_competition()
            comp_name = comp.name if comp else f"#{reg.competition_id}"
            text = message_template.format(competition=comp_name)

            try:
                payload = json.dumps({'chat_id': telegram_id, 'text': text}).encode('utf-8')
                req = urllib.request.Request(api_url, data=payload, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=10)
            except Exception as e:
                logger.error(f"Notification error for {telegram_id}: {e}")

    def approve_registrations(self, request, queryset):
        pending = list(queryset.filter(status='pending'))
        updated = queryset.filter(status='pending').update(status='approved')
        if pending:
            self._notify_users(pending, "Ваша заявка на участие в «{competition}» одобрена!")
        self.message_user(request, f'✅ Одобрено {updated} заявок.')
    approve_registrations.short_description = 'Одобрить выбранные заявки'

    def reject_registrations(self, request, queryset):
        pending = list(queryset.filter(status='pending'))
        updated = queryset.filter(status='pending').update(status='rejected')
        if pending:
            self._notify_users(pending, "К сожалению, ваша заявка на участие в «{competition}» отклонена.")
        self.message_user(request, f'❌ Отклонено {updated} заявок.')
    reject_registrations.short_description = 'Отклонить выбранные заявки'

    def revoke_registrations(self, request, queryset):
        approved = list(queryset.filter(status='approved'))
        updated = queryset.filter(status='approved').update(status='pending', is_confirmed=False)
        if approved:
            self._notify_users(approved, "Ваша заявка на участие в «{competition}» отозвана и ожидает повторного рассмотрения.")
        self.message_user(request, f'⚠️ Отозвано {updated} заявок (статус: на рассмотрении).')
    revoke_registrations.short_description = '⚠️ Отозвать одобренные заявки'

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f'✔️ Подтверждено {updated} заявок.')
    mark_as_confirmed.short_description = 'Отметить как подтвержденные'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):

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
        return obj.get_competition()
    get_competition_name.short_description = 'Соревнование'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'✅ Временной слот обновлен: {obj.slot_day} {obj.start_time}-{obj.end_time}')
        else:
            self.message_user(request, f'✅ Временной слот создан: {obj.slot_day} {obj.start_time}-{obj.end_time}')

@admin.register(JuryPanel)
class JuryPanelAdmin(admin.ModelAdmin):

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
        return obj.get_competition()
    get_competition_name.short_description = 'Соревнование'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'✅ Судейская коллегия обновлена: {obj.panel_name}')
        else:
            self.message_user(request, f'✅ Судейская коллегия создана: {obj.panel_name}')

admin.site.site_header = "USN Telegram Bot - Администрирование"
admin.site.site_title = "Админка бота"
admin.site.index_title = "Добро пожаловать в панель администрирования"

from django.contrib.auth.models import User as AuthUser, Group
admin.site.unregister(AuthUser)
admin.site.unregister(Group)
