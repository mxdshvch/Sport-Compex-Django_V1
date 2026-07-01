from django.urls import path
from . import views, admin_views
from . import chat_views

urlpatterns = [
    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Личный кабинет
    path('account/', views.profile_view, name='account_home'),
    path('account/profile/', views.profile_view, name='account_profile'),
    path('account/profile/edit/', views.edit_profile_view, name='account_edit_profile'),
    path('account/profile/change-password/', views.change_password_view, name='account_change_password'),
    path('account/schedule/', views.schedule_view, name='account_schedule'),
    path('account/schedule/register/<int:workout_id>/', views.register_for_workout, name='register_for_workout'),
    path('account/schedule/cancel/<int:registration_id>/', views.cancel_workout_registration, name='cancel_workout_registration'),
    path('account/trainers/', views.trainers_view, name='account_trainers'),
    
    # Заявки пользователей
    path('account/requests/', views.requests_view, name='account_requests'),
    path('account/requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('account/requests/create/', views.create_request, name='create_request'),
    path('account/requests/<int:request_id>/send/', views.send_message, name='send_message'),
    path('account/requests/<int:request_id>/messages/', views.get_new_messages, name='get_new_messages'),
    
    # Старые URL для совместимости (редиректы)
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('trainers/', views.trainers_view, name='trainers'),
    path('requests/', views.requests_view, name='requests'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/create/', views.create_request, name='create_request'),
    
    # Административные маршруты для заявок
    path('admin/user_requests/', admin_views.admin_requests, name='admin_requests'),
    path('admin/user_requests/<int:request_id>/', admin_views.admin_request_detail, name='admin_request_detail'),
    path('admin/user_requests/<int:request_id>/data/', admin_views.load_request_data, name='load_request_data'),
    path('admin/user_requests/<int:request_id>/message/', admin_views.send_message, name='admin_send_message'),
    path('admin/user_requests/<int:request_id>/complete/', admin_views.complete_request, name='complete_request'),
    path('admin/user_requests/<int:request_id>/status/', admin_views.update_request_status, name='update_request_status'),
    path('admin/user_requests/<int:request_id>/new-messages/', admin_views.get_new_messages, name='get_new_messages'),
    path('admin/user_requests/check-updates/', admin_views.check_request_updates, name='check_request_updates'),
] 