"""
URL configuration for fitness_center project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
import os
# Импортируем admin_index для инициализации кастомного admin.site
import fitness_center.admin_index
# Импортируем представления для заявок пользователей
from users.admin_views import admin_requests, load_request_data, send_message as admin_send_message, complete_request as admin_complete_request, get_new_messages as admin_get_new_messages, check_request_updates as admin_check_updates
from users.chat_views import chat_view, send_message, complete_request, get_new_messages
from trainers.views import search_trainers, delete_trainer
# Импортируем представление для поиска заявок на абонементы
from memberships.views import admin_application_search

# Получаем путь к каталогу проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Middleware для защиты всех URL админки
class AdminAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Проверяем, начинается ли путь с /admin/
        if request.path.startswith('/admin/'):
            # Исключаем статические файлы и ресурсы, которые не требуют аутентификации
            if '/static/' in request.path or '/media/' in request.path:
                return None
                
            # Если пользователь не авторизован или не является администратором
            if not request.user.is_authenticated or not request.user.is_staff:
                # Перенаправляем на главную страницу
                return HttpResponseRedirect('/')
        return None

# Функция для проверки прав администратора и перенаправления
def admin_redirect(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Если пользователь - администратор, перенаправляем на страницу администратора
        return HttpResponseRedirect('/admin/')
    else:
        # Если обычный пользователь, перенаправляем на главную страницу
        return HttpResponseRedirect('/')

urlpatterns = [
    # Перенаправление с /admin (без слеша) в зависимости от прав пользователя
    path('admin', admin_redirect),
    
    # Административные URL для заявок пользователей
    path('admin/user_requests/', admin_requests, name='admin_requests'),
    path('admin/user_requests/load/<int:request_id>/', load_request_data, name='admin_load_request_data'),
    path('admin/user_requests/<int:request_id>/send/', admin_send_message, name='admin_send_message'),
    path('admin/user_requests/<int:request_id>/complete/', admin_complete_request, name='admin_complete_request'),
    path('admin/user_requests/<int:request_id>/messages/', admin_get_new_messages, name='admin_get_new_messages'),
    path('admin/user_requests/check_updates/', admin_check_updates, name='admin_check_request_updates'),
    
    # URL для AJAX поиска тренеров в админке
    path('admin/trainers/search/', search_trainers, name='search_trainers'),
    
    # URL для AJAX удаления тренера в админке
    path('admin/trainers/trainer/<int:trainer_id>/delete/', delete_trainer, name='delete_trainer'),
    
    # URL для AJAX поиска заявок на абонементы в админке
    path('admin/memberships/membershipapplication/search/', admin_application_search, name='admin_application_search_direct'),
    
    # Стандартные URL админки
    path('admin/', admin.site.urls),
    
    # Перенаправление с /admin/auth/user/ на /admin/users/customuser/
    re_path(r'^admin/auth/user/$', RedirectView.as_view(url='/admin/users/customuser/', permanent=True)),
    re_path(r'^admin/auth/user/add/$', RedirectView.as_view(url='/admin/users/customuser/add/', permanent=True)),
    re_path(r'^admin/auth/user/(?P<id>\d+)/change/$', 
            RedirectView.as_view(url='/admin/users/customuser/%(id)s/change/', permanent=True)),
    
    # Основные URL-маршруты
    path('', include('workouts.urls')),  # workouts обрабатывает главную страницу
    path('users/', include('users.urls')),
    path('memberships/', include('memberships.urls')),
    path('trainers/', include('trainers.urls')),
    
    # Чат URLs
    path('chat/<int:request_id>/', chat_view, name='chat_view'),
    path('chat/<int:request_id>/send/', send_message, name='send_message'),
    path('chat/<int:request_id>/complete/', complete_request, name='complete_request'),
    path('chat/<int:request_id>/messages/', get_new_messages, name='get_new_messages'),
    
    # Личный кабинет пользователя
    path('account/', include('users.account_urls')),
    
    # Прямой доступ к чату без шапки и подвала
    path('chat-minimal/', include([
        path('', RedirectView.as_view(url='/account/requests/', permanent=False), name='chat_minimal'),
        path('<int:request_id>/', lambda request, request_id: RedirectView.as_view(
            url=f'/account/requests/?request_id={request_id}', 
            permanent=False
        )(request), name='chat_minimal_with_id'),
    ])),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Добавляем URL для Debug Toolbar если DEBUG=True
if settings.DEBUG:
    # Debug Toolbar отключен
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns
    pass
