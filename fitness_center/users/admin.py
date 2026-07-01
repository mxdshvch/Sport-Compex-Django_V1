from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRequest
from .forms import CustomUserCreationForm
from django.utils.translation import gettext_lazy as _
from fitness_center.admin import SaveOnlyModelAdmin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.db.models import Count


class CustomUserAdmin(UserAdmin, SaveOnlyModelAdmin):
    """
    Настройка отображения пользовательской модели в админке.
    """
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ('email', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    list_per_page = 20  # Уменьшаем количество записей на странице
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {'fields': ('name',)}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    # Переопределяем методы из UserAdmin, чтобы использовать функциональность SaveOnlyModelAdmin
    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect('../')
    
    def response_change(self, request, obj):
        return HttpResponseRedirect('../')
        
    def changelist_view(self, request, extra_context=None):
        """
        Упрощенный метод без добавления лишних данных в контекст
        """
        return super().changelist_view(request, extra_context)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(UserRequest)
class UserRequestAdmin(SaveOnlyModelAdmin):
    """
    Администрирование заявок пользователей
    """
    list_display = ('user', 'title', 'created_at', 'status_badge', 'has_response')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'user__email', 'user__name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20  # Уменьшаем количество записей на странице
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'status', 'admin_response')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        """
        Оптимизируем запрос с помощью select_related для поля user
        """
        return super().get_queryset(request).select_related('user')
    
    def status_badge(self, obj):
        """Отображение статуса в виде цветной метки"""
        status_colors = {
            'new': 'primary',
            'in_progress': 'warning',
            'completed': 'success',
            'rejected': 'danger',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge" style="background-color: var(--bs-{});">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    
    def has_response(self, obj):
        """Отображает, есть ли ответ на заявку"""
        if obj.admin_response:
            return format_html('<span style="color: green; font-size: 18px;">✓</span>')
        return format_html('<span style="color: red; font-size: 18px;">✕</span>')
    has_response.short_description = 'Ответ'
