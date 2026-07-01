from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользовательской модели, где email является уникальным идентификатором
    вместо username.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Создать и сохранить пользователя с указанным email и паролем.
        """
        if not email:
            raise ValueError(_('Email должен быть установлен'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создать и сохранить суперпользователя с указанным email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Модель пользователя с email в качестве основного идентификатора
    вместо имени пользователя.
    """
    username = None
    email = models.EmailField(_('email адрес'), unique=True)
    name = models.CharField(_('имя'), max_length=100)
    profile_image = models.ImageField(_('фото профиля'), upload_to='profile_images/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


class UserRequest(models.Model):
    """
    Модель для заявок пользователей
    """
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(_('заголовок'), max_length=200)
    description = models.TextField(_('описание'))
    status = models.CharField(_('статус'), max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    admin_response = models.TextField(_('ответ администратора'), blank=True, null=True)

    class Meta:
        verbose_name = _('заявка пользователя')
        verbose_name_plural = _('заявки пользователей')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.title}"


class ChatMessage(models.Model):
    """
    Модель для сообщений в чате между пользователем и администратором
    """
    request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField(_('сообщение'))
    created_at = models.DateTimeField(_('дата отправки'), auto_now_add=True)
    is_read = models.BooleanField(_('прочитано'), default=False)
    is_system = models.BooleanField(_('системное сообщение'), default=False)

    class Meta:
        verbose_name = _('сообщение чата')
        verbose_name_plural = _('сообщения чата')
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение от {self.sender.name} в заявке {self.request.title}"
