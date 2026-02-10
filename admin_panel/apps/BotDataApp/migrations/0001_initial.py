"""
Initial migrations for BotDataApp.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotDashboardStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stat_name', models.CharField(max_length=100, unique=True)),
                ('stat_value', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Dashboard Statistic',
                'verbose_name_plural': 'Dashboard Statistics',
            },
        ),
        migrations.CreateModel(
            name='AdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.BigIntegerField()),
                ('action', models.CharField(choices=[('approve', 'Approved Registration'), ('reject', 'Rejected Registration'), ('revoke', 'Revoked Registration'), ('update_competition', 'Updated Competition'), ('delete_user', 'Deleted User'), ('other', 'Other')], max_length=20)),
                ('target_type', models.CharField(max_length=50)),
                ('target_id', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Admin Log',
                'verbose_name_plural': 'Admin Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]