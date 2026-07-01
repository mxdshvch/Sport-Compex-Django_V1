from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Membership(models.Model):
    """
    Модель для абонементов фитнес-центра.
    """
    name = models.CharField(_('название'), max_length=200)
    description = models.TextField(
        _('описание'),
        blank=True,
        null=True
    )
    price = models.DecimalField(_('цена'), max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(_('срок действия (в днях)'))
    image = models.ImageField(_('изображение'), upload_to='memberships/', null=True, blank=True, 
                            help_text=_('Изображение для карточки абонемента'))
    
    class Meta:
        verbose_name = _('абонемент')
        verbose_name_plural = _('абонементы')
    
    def __str__(self):
        return f"{self.name} - {self.price} руб."


class MembershipApplication(models.Model):
    """
    Модель для заявок на приобретение абонемента.
    """
    STATUS_CHOICES = (
        ('pending', _('В обработке')),
        ('approved', _('Одобрено')),
        ('rejected', _('Отклонено')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('пользователь'),
        on_delete=models.CASCADE,
        related_name='membership_applications',
        null=True,
        blank=True
    )
    membership = models.ForeignKey(
        Membership,
        verbose_name=_('абонемент'),
        on_delete=models.CASCADE,
        related_name='applications'
    )
    name = models.CharField(_('имя'), max_length=200)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('телефон'), max_length=20)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    class Meta:
        verbose_name = _('заявка на абонемент')
        verbose_name_plural = _('заявки на абонементы')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка на {self.membership} от {self.name}"
