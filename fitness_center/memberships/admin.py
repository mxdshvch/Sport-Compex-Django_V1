from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Membership, MembershipApplication
from fitness_center.admin import SaveOnlyModelAdmin
from django.contrib import messages
from django.utils.html import format_html
from .forms import MembershipAdminForm
from django.core.cache import cache


@admin.register(Membership)
class MembershipAdmin(SaveOnlyModelAdmin):
    list_display = ('name', 'price', 'duration', 'has_image')
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'price', 'duration', 'image')
    readonly_fields = ()
    form = MembershipAdminForm

    def has_image(self, obj):
        """Показывает, загружено ли изображение для абонемента."""
        if obj.image:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✕</span>')
    has_image.short_description = 'Изображение'
    
    def has_add_permission(self, request):
        """
        Проверяет, можно ли добавить новый абонемент.
        Ограничивает количество абонементов до 3.
        """
        if Membership.objects.count() >= 3:
            return False
        return super().has_add_permission(request)
    
    def save_model(self, request, obj, form, change):
        """
        Дополнительная проверка перед сохранением, чтобы избежать обхода ограничения.
        """
        if not change and Membership.objects.count() >= 3:
            return
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        """
        Добавляем список абонементов в контекст шаблона
        """
        # Создаем контекст или обновляем существующий
        context = extra_context or {}
        
        # Убираем предупреждение о максимальном количестве абонементов
        
        return super().changelist_view(request, context)
    
    def get_queryset(self, request):
        """
        Переопределяем метод get_queryset для правильного отображения абонементов
        """
        return Membership.objects.all()


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(SaveOnlyModelAdmin):
    list_display = ('name', 'email', 'phone', 'membership_name', 'status_display', 'created_at')
    list_filter = ('status',)  # Упрощаем фильтры для ускорения
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    list_per_page = 10  # Уменьшаем количество записей на странице для ускорения загрузки
    
    def membership_name(self, obj):
        """Отображает название абонемента без лишних запросов"""
        if hasattr(obj, 'membership') and obj.membership:
            return obj.membership.name
        return "-"
    membership_name.short_description = 'Абонемент'
    
    def status_display(self, obj):
        """
        Отображение статуса заявки с соответствующим цветом.
        Упрощенная версия без лишних классов CSS.
        """
        status_colors = {
            'pending': '#FFA500',  # Оранжевый для "В обработке"
            'approved': '#28a745',  # Зеленый для "Одобрено"
            'rejected': '#dc3545',  # Красный для "Отклонено"
        }
        status_texts = {
            'pending': 'В обработке',
            'approved': 'Одобрено',
            'rejected': 'Отклонено',
        }
        
        color = status_colors.get(obj.status, '#6c757d')  # Серый по умолчанию
        text = status_texts.get(obj.status, obj.get_status_display())
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    status_display.short_description = 'Статус'
    
    def get_queryset(self, request):
        """
        Оптимизируем запрос с помощью select_related и применяем фильтрацию
        """
        # Проверяем кэш
        cache_key = f'membership_applications_queryset_{request.GET.get("status", "all")}'
        cached_queryset = cache.get(cache_key)
        
        if cached_queryset is not None:
            return cached_queryset
        
        # Если в кэше нет, выполняем запрос
        queryset = super().get_queryset(request).select_related('membership')
        
        # Применяем фильтрацию только если есть параметр status в запросе
        status_filter = request.GET.get('status')
        if status_filter and status_filter in dict(MembershipApplication.STATUS_CHOICES).keys():
            queryset = queryset.filter(status=status_filter)
        
        # Кэшируем результат на 1 минуту
        cache.set(cache_key, queryset, 60)
        
        return queryset
    
    def changelist_view(self, request, extra_context=None):
        """
        Упрощенный метод без добавления лишних данных в контекст
        """
        # Отключаем date_hierarchy для ускорения загрузки
        self.date_hierarchy = None
        
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('css/admin/membership_application.css',)
        }
        js = ('js/admin/membership_application.js',)
