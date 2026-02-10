"""
URL configuration for Bot Data Management App.
"""
from django.urls import path
from . import views

app_name = 'bot_data'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('registrations/', views.RegistrationsView.as_view(), name='registrations'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('competitions/', views.CompetitionsView.as_view(), name='competitions'),

    path('api/stats/', views.bot_stats_api, name='stats_api'),
    path('api/registration/<int:registration_id>/', views.registration_detail, name='registration_detail'),
]
