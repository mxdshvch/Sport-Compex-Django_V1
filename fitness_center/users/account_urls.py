from django.urls import path
from . import views
from . import chat_views

urlpatterns = [
    # Основные страницы личного кабинета
    path('', views.profile_view, name='account_home'),  # Домашняя страница кабинета
    path('profile/', views.profile_view, name='account_profile'),
    path('profile/change-password/', views.change_password_view, name='account_change_password'),
    path('schedule/', views.schedule_view, name='account_schedule'),
    path('trainers/', views.trainers_view, name='account_trainers'),
    path('requests/', views.requests_view, name='account_requests'),
    
    # Функциональные URL
    path('schedule/register/<int:workout_id>/', views.register_for_workout, name='account_register_for_workout'),
    path('schedule/cancel/<int:registration_id>/', views.cancel_workout_registration, name='account_cancel_workout_registration'),
    
    # URL для чата
    path('requests/<int:request_id>/send/', views.send_message, name='account_send_message'),
    path('requests/<int:request_id>/messages/', views.get_messages, name='account_get_messages'),
    path('requests/load/<int:request_id>/', chat_views.load_request_data, name='account_load_request_data'),
] 