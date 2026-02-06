"""
Views for Bot Data Management.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
import json

from .models import SQLiteDataHelper, AdminLog


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view with bot statistics."""

    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Bot statistics
            context['user_count'] = SQLiteDataHelper.get_user_count()
            context['competition_count'] = SQLiteDataHelper.get_competition_count()
            context['registration_count'] = SQLiteDataHelper.get_registration_count()
            context['reg_by_status'] = SQLiteDataHelper.get_registrations_by_status()
            context['recent_registrations'] = SQLiteDataHelper.get_recent_registrations(10)
            context['users_by_role'] = SQLiteDataHelper.get_users_by_role()
            context['active_competitions'] = SQLiteDataHelper.get_active_competitions()

            # Admin logs
            context['recent_logs'] = AdminLog.objects.all()[:10]
        except Exception as e:
            context['error'] = f"Failed to load statistics: {str(e)}"

        return context


class RegistrationsView(LoginRequiredMixin, TemplateView):
    """View for managing registrations."""

    template_name = 'admin_panel/registrations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['all_registrations'] = SQLiteDataHelper.execute_raw_query(
                """
                SELECT r.id, r.user_id, r.competition_id, r.role, r.status,
                       r.created_at, u.first_name, u.last_name, u.telegram_id,
                       c.name as competition_name
                FROM registrations r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN competitions c ON r.competition_id = c.id
                ORDER BY r.id DESC
                """
            )
            context['statuses'] = ['pending', 'approved', 'rejected']
        except Exception as e:
            context['error'] = str(e)

        return context


class UsersView(LoginRequiredMixin, TemplateView):
    """View for managing users."""

    template_name = 'admin_panel/users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['all_users'] = SQLiteDataHelper.execute_raw_query(
                """
                SELECT u.id, u.telegram_id, u.username, u.first_name, u.last_name,
                       u.phone, u.email, u.created_at,
                       COUNT(r.id) as registration_count
                FROM users u
                LEFT JOIN registrations r ON u.id = r.user_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            )
        except Exception as e:
            context['error'] = str(e)

        return context


class CompetitionsView(LoginRequiredMixin, TemplateView):
    """View for managing competitions."""

    template_name = 'admin_panel/competitions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['all_competitions'] = SQLiteDataHelper.execute_raw_query(
                """
                SELECT c.id, c.name, c.type, c.is_active, c.created_at,
                       COUNT(r.id) as registration_count
                FROM competitions c
                LEFT JOIN registrations r ON c.id = r.competition_id
                GROUP BY c.id
                ORDER BY c.created_at DESC
                """
            )
        except Exception as e:
            context['error'] = str(e)

        return context


@login_required
def bot_stats_api(request):
    """API endpoint for bot statistics."""
    try:
        data = {
            'users': SQLiteDataHelper.get_user_count(),
            'competitions': SQLiteDataHelper.get_competition_count(),
            'registrations': SQLiteDataHelper.get_registration_count(),
            'registrations_by_status': SQLiteDataHelper.get_registrations_by_status(),
            'users_by_role': SQLiteDataHelper.get_users_by_role(),
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def registration_detail(request, registration_id):
    """Get registration details via API."""
    try:
        result = SQLiteDataHelper.execute_raw_query(
            """
            SELECT r.id, r.user_id, r.competition_id, r.role, r.status,
                   r.created_at, r.is_confirmed,
                   u.first_name, u.last_name, u.telegram_id, u.email, u.phone,
                   c.name as competition_name
            FROM registrations r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN competitions c ON r.competition_id = c.id
            WHERE r.id = ?
            """,
            [registration_id]
        )

        if result:
            return JsonResponse({'success': True, 'data': result[0]})
        else:
            return JsonResponse({'success': False, 'error': 'Registration not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)