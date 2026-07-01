from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from users.models import CustomUser
from trainers.models import Trainer
from django.utils import timezone
# from django_summernote.fields import SummernoteTextField


class TrainingGoal(models.Model):
    """
    Модель для целей тренировок (например, похудение, набор массы, и т.д.).
    """
    name = models.CharField(_('название'), max_length=100)
    
    class Meta:
        verbose_name = _('цель тренировки')
        verbose_name_plural = _('цели тренировок')
    
    def __str__(self):
        return self.name


class WorkoutDirection(models.Model):
    """
    Модель для направлений тренировок.
    """
    name = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'), help_text=_('Используйте панель инструментов для форматирования текста: жирный текст, курсив, списки и другие элементы форматирования.'))
    image = models.ImageField(_('изображение'), upload_to='workout_directions/')
    goals = models.ManyToManyField(
        TrainingGoal,
        verbose_name=_('цели тренировки'),
        related_name='directions',
        blank=True
    )
    
    class Meta:
        verbose_name = _('направление тренировок')
        verbose_name_plural = _('направления тренировок')
    
    def __str__(self):
        return self.name


class Workout(models.Model):
    """
    Модель тренировки
    """
    HALL_CHOICES = [
        ('small', 'Малый зал'),
        ('large', 'Большой зал'),
    ]
    
    title = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'))
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='workouts')
    date = models.DateField(_('дата'))
    time = models.TimeField(_('время'))
    duration = models.IntegerField(_('длительность (минуты)'))
    max_participants = models.IntegerField(_('максимальное количество участников'))
    hall = models.CharField(_('зал'), max_length=10, choices=HALL_CHOICES, default='small')
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('тренировка')
        verbose_name_plural = _('тренировки')
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"
    
    @property
    def is_full(self):
        """
        Проверяет, заполнена ли тренировка до максимума
        """
        return self.registrations.filter(is_active=True).count() >= self.max_participants
    
    @property
    def is_past(self):
        """
        Проверяет, прошла ли тренировка
        """
        now = timezone.now()
        workout_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return workout_datetime < now
    
    @property
    def is_registration_closed(self):
        """
        Проверяет, закрыта ли запись на тренировку (менее часа до начала)
        """
        now = timezone.now()
        workout_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        time_before_start = workout_datetime - now
        return time_before_start.total_seconds() < 3600  # менее часа (3600 секунд)
    
    @property
    def can_register(self):
        """
        Проверяет, можно ли записаться на тренировку
        """
        return not self.is_past and not self.is_registration_closed and not self.is_full
    
    def get_user_registration(self, user=None):
        """
        Возвращает активную регистрацию пользователя на эту тренировку
        """
        if not user:
            from django.contrib.auth.models import AnonymousUser
            if isinstance(user, AnonymousUser):
                return None
            
            # Если user передан как None, но на самом деле это request.user
            from django.utils.functional import SimpleLazyObject
            if isinstance(user, SimpleLazyObject):
                user = user._wrapped
        
        try:
            return self.registrations.get(user=user, is_active=True)
        except:
            return None


class WorkoutRegistration(models.Model):
    """
    Модель записи на тренировку
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='workout_registrations')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(_('дата записи'), auto_now_add=True)
    is_active = models.BooleanField(_('активна'), default=True)

    class Meta:
        verbose_name = _('запись на тренировку')
        verbose_name_plural = _('записи на тренировки')
        unique_together = ['user', 'workout']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.workout.title}"
