from django.contrib import admin
from .models import Trainer
from fitness_center.admin import SaveOnlyModelAdmin


@admin.register(Trainer)
class TrainerAdmin(SaveOnlyModelAdmin):
    list_display = ('name', 'specialization')
    search_fields = ('name', 'specialization', 'description')
    list_per_page = 50  # Ограничиваем количество записей на странице
