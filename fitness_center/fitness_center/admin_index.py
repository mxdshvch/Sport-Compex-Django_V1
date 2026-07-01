from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from users.models import CustomUser, UserRequest
from trainers.models import Trainer
from workouts.models import Workout
from memberships.models import MembershipApplication
from django.db.models import Count


class CustomAdminSite(AdminSite):
    """
    Кастомный сайт админки с переопределенным методом index для показа статистики
    """
    
    def index(self, request, extra_context=None):
        # Используем select_related для оптимизации запросов
        # Подсчет новых заявок (заявки в статусе "В обработке")
        new_applications_count = MembershipApplication.objects.filter(status='pending').count()
        
        # Количество активных заявок пользователей - оптимизированный запрос
        user_requests_count = UserRequest.objects.filter(status__in=['new', 'in_progress']).count()
        
        # Остальные запросы
        trainers_count = Trainer.objects.count()
        workouts_count = Workout.objects.count()
        users_count = CustomUser.objects.count()
        
        context = {
            'new_applications_count': new_applications_count,
            'user_requests_count': user_requests_count,
            'trainers_count': trainers_count,
            'workouts_count': workouts_count,
            'users_count': users_count,
        }
        
        if extra_context:
            context.update(extra_context)
        
        return super().index(request, context)


# Сохраняем копию оригинального admin.site и его зарегистрированных моделей
old_site = admin.site
old_registry = admin.site._registry.copy()

# Создаем новый экземпляр CustomAdminSite
custom_admin_site = CustomAdminSite(name='admin')

# Заменяем стандартный AdminSite на наш кастомный
admin.site = custom_admin_site

# Регистрируем все модели из старого реестра в новом admin.site
for model, model_admin in old_registry.items():
    admin.site.register(model, model_admin.__class__) 