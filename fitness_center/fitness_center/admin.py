from django.contrib import admin
from django.http import HttpResponseRedirect
from trainers.models import Trainer
from workouts.models import Workout
from users.models import CustomUser, UserRequest
from memberships.models import MembershipApplication
from django.contrib.admin import AdminSite
from django.core.cache import cache
from django.utils import timezone
import datetime


class SaveOnlyModelAdmin(admin.ModelAdmin):
    """
    Модификация ModelAdmin, которая делает редирект сразу на список объектов
    после сохранения вместо показа страницы с сохраненным объектом.
    """
    save_on_top = False
    
    def response_add(self, request, obj, post_url_continue=None):
        """
        Перенаправляет на список после добавления объекта
        """
        return HttpResponseRedirect('../')
    
    def response_change(self, request, obj):
        """
        Перенаправляет на список после изменения объекта
        """
        return HttpResponseRedirect('../')
    
    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель и выводит сообщение об успешном сохранении
        """
        super().save_model(request, obj, form, change)
        
    def get_changeform_initial_data(self, request):
        """
        Получает начальные данные формы изменения
        """
        return super().get_changeform_initial_data(request) 


# Переопределение главной страницы административной панели
admin.site.index_template = 'admin/index.html'

# Вызывается при отображении главной страницы административной панели
def get_admin_stats(request):
    """
    Получает статистику для главной страницы административной панели.
    Вызывается через шаблон admin/index.html.
    Результаты кэшируются на 5 минут для ускорения загрузки.
    """
    # Проверяем кэш
    cache_key = 'admin_stats'
    cached_stats = cache.get(cache_key)
    
    if cached_stats:
        return cached_stats
    
    # Если в кэше нет данных, запрашиваем их из базы
    context = {
        'users_count': CustomUser.objects.count(),
        'trainers_count': Trainer.objects.count(),
        'workouts_count': Workout.objects.count(),
        'new_applications_count': MembershipApplication.objects.filter(status='pending').count(),
        'user_requests_count': UserRequest.objects.filter(status='new').count(),
    }
    
    # Кэшируем результаты на 5 минут
    cache.set(cache_key, context, 300)  # 300 секунд = 5 минут
    
    return context

# Добавляем context_processor для админки
original_each_context = AdminSite.each_context

def custom_each_context(self, request):
    context = original_each_context(self, request)
    if request.path == '/admin/':
        context.update(get_admin_stats(request))
    return context

AdminSite.each_context = custom_each_context

# Переопределяем стили для админки, чтобы использовать Roboto
class CustomAdminSite(AdminSite):
    """
    Кастомная админка с поддержкой шрифта Roboto
    """
    
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'has_roboto_font': True,
            'roboto_css': '/static/admin/css/custom_admin.css',
        })
        return context

# Применяем кастомные стили к стандартной админке
original_get_app_list = AdminSite.get_app_list

def custom_get_app_list(self, request):
    app_list = original_get_app_list(self, request)
    # Добавляем CSS для Roboto в контекст
    if not hasattr(request, 'roboto_css_added'):
        request.roboto_css_added = True
        # Здесь можно модифицировать app_list если нужно
    return app_list

AdminSite.get_app_list = custom_get_app_list

# Регистрируем хук для добавления CSS в админку
from django.contrib.admin.templatetags.admin_modify import submit_row
from django.template.loader import render_to_string

original_submit_row = submit_row

def custom_submit_row(context):
    # Добавляем CSS для Roboto в контекст
    context.update({
        'has_roboto_font': True,
        'roboto_css': '/static/admin/css/custom_admin.css',
    })
    return original_submit_row(context)

# Заменяем стандартный тег на наш кастомный
from django.template.library import Library
from django.contrib.admin.templatetags.admin_modify import register

register.simple_tag(takes_context=True)(custom_submit_row) 