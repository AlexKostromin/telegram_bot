import os
import sys
from django.db import models, connection
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from models.user import User as SQLAlchemyUser
    from models.competition import Competition as SQLAlchemyCompetition
    from models.registration import Registration as SQLAlchemyRegistration
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

class CompetitionManager(models.Manager):

    def get_active(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM competitions WHERE is_active = 1")
            return cursor.fetchall()

    def get_with_stats(self):
        with connection.cursor() as cursor:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

class RegistrationManager(models.Manager):

    def pending(self):
        with connection.cursor() as cursor:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def approved(self):
        with connection.cursor() as cursor:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

class Competition(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, null=True, blank=True)
    competition_type = models.CharField(max_length=50)
    available_roles = models.JSONField(null=True, blank=True)
    player_entry_open = models.BooleanField(default=False)
    voter_entry_open = models.BooleanField(default=False)
    viewer_entry_open = models.BooleanField(default=False)
    adviser_entry_open = models.BooleanField(default=False)
    requires_time_slots = models.BooleanField(default=False)
    requires_jury_panel = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CompetitionManager()

    class Meta:
        managed = False
        db_table = 'competitions'
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'

    def __str__(self):
        return f"{self.name} ({self.type})"

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

class User(models.Model):

    id = models.IntegerField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    club = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    certificate_name = models.CharField(max_length=255, null=True, blank=True)
    presentation = models.CharField(max_length=500, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    channel_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else f"User #{self.telegram_id}"

    def registration_count(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE user_id = %s",
                [self.id]
            )
            return cursor.fetchone()[0]

class Registration(models.Model):

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

    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    telegram_id = models.BigIntegerField(null=True, blank=True)
    competition_id = models.IntegerField()
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegistrationManager()

    class Meta:
        managed = False
        db_table = 'registrations'
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        ordering = ['-id']

    def __str__(self):
        return f"Регистрация #{self.id} ({self.get_status_display()})"

    def user(self):
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    def competition(self):
        try:
            return Competition.objects.get(id=self.competition_id)
        except Competition.DoesNotExist:
            return None
