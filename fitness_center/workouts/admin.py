from django.contrib import admin
from .models import WorkoutDirection, Workout, TrainingGoal
from fitness_center.admin import SaveOnlyModelAdmin
from django.utils.html import format_html
from .forms import WorkoutDirectionAdminForm, WorkoutAdminForm


@admin.register(TrainingGoal)
class TrainingGoalAdmin(SaveOnlyModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class TrainingGoalInline(admin.TabularInline):
    model = WorkoutDirection.goals.through
    verbose_name = "Цель тренировки"
    verbose_name_plural = "Цели тренировок"
    extra = 1


@admin.register(WorkoutDirection)
class WorkoutDirectionAdmin(SaveOnlyModelAdmin):
    form = WorkoutDirectionAdminForm
    list_display = ('name', 'description_preview', 'display_goals')
    search_fields = ('name', 'description')
    filter_horizontal = ('goals',)
    
    def description_preview(self, obj):
        """Предпросмотр описания с ограничением длины"""
        if obj.description:
            if len(obj.description) > 100:
                return obj.description[:100] + '...'
            return obj.description
        return '-'
    description_preview.short_description = 'Описание'
    
    def display_goals(self, obj):
        """Отображает список целей тренировки"""
        goals = list(obj.goals.values_list('name', flat=True)[:3])  # Ограничиваем количество целей для отображения
        if goals:
            goals_str = ', '.join(goals)
            if obj.goals.count() > 3:
                goals_str += '...'
            return goals_str
        return '-'
    display_goals.short_description = 'Цели тренировки'
    
    class Media:
        css = {
            'all': ('css/admin/workout_direction.css',)
        }
    

@admin.register(Workout)
class WorkoutAdmin(SaveOnlyModelAdmin):
    form = WorkoutAdminForm
    list_display = ('title', 'trainer', 'date', 'time', 'duration', 'max_participants', 'get_hall_display')
    list_filter = ('trainer', 'date', 'hall')
    search_fields = ('title', 'trainer__name')
    date_hierarchy = 'date'
    list_per_page = 20  # Уменьшаем количество записей на странице
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'trainer')
        }),
        ('Расписание', {
            'fields': ('date', 'time', 'duration')
        }),
        ('Дополнительно', {
            'fields': ('max_participants', 'hall')
        })
    )
    
    def get_queryset(self, request):
        """
        Оптимизируем запрос с помощью select_related для поля trainer
        """
        return super().get_queryset(request).select_related('trainer')
    
    class Media:
        css = {
            'all': ('css/admin/workouts.css',)
        }
    
    def get_hall_display(self, obj):
        """Отображает зал с цветовой индикацией"""
        hall_colors = {
            'small': '#28a745',  # зеленый для малого зала
            'large': '#007bff',  # синий для большого зала
        }
        hall_display = dict(obj.HALL_CHOICES).get(obj.hall, obj.hall)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px;">{}</span>',
            hall_colors.get(obj.hall, '#6c757d'),
            hall_display
        )
    get_hall_display.short_description = "Зал"
