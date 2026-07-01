from django.db import models
from django.utils.translation import gettext_lazy as _
# from django_summernote.fields import SummernoteTextField


class Trainer(models.Model):
    """
    Модель для тренеров фитнес-центра.
    """
    name = models.CharField(_('имя'), max_length=200)
    photo = models.ImageField(_('фото'), upload_to='trainers/')
    specialization = models.CharField(_('специализация'), max_length=200)
    description = models.TextField(_('описание'))
    
    class Meta:
        verbose_name = _('тренер')
        verbose_name_plural = _('тренеры')
    
    def __str__(self):
        return self.name
        
    def get_upcoming_workouts(self):
        """
        Получить ближайшие тренировки тренера.
        """
        from django.utils import timezone
        return self.workouts.filter(date__gte=timezone.now().date()).order_by('date', 'start_time')
