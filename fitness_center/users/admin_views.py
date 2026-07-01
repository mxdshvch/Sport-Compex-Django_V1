from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Case, When, IntegerField, Prefetch
from .models import UserRequest, ChatMessage
from django.urls import reverse
from django.views.decorators.http import require_POST
import json
from django.template.loader import get_template
from django.core.cache import cache

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_requests(request):
    """
    Представление для административного интерфейса заявок
    """
    # Используем упрощенный шаблон без тяжелых JavaScript компонентов
    # и получаем только список заявок
    
    # Получаем активные (новые и в обработке) заявки, ограничиваем до 30
    active_requests = UserRequest.objects.select_related('user').filter(
        status__in=['new', 'in_progress']
    ).annotate(
        unread_messages=Count(
            Case(
                When(messages__is_read=False, messages__sender__is_staff=False, then=1),
                output_field=IntegerField(),
            )
        )
    ).order_by('-created_at')[:30]

    # Получаем завершенные заявки, ограничиваем до 20 для улучшения производительности
    completed_requests = UserRequest.objects.select_related('user').filter(
        status='completed'
    ).order_by('-updated_at')[:20]

    # Вычисляем счетчики отдельно
    active_requests_count = UserRequest.objects.filter(
        status__in=['new', 'in_progress']
    ).count()
    
    completed_requests_count = UserRequest.objects.filter(
        status='completed'
    ).count()

    context = {
        'active_requests': active_requests,
        'completed_requests': completed_requests,
        'active_requests_count': active_requests_count,
        'completed_requests_count': completed_requests_count,
        'title': 'Заявки пользователей'
    }
    
    return render(request, 'admin/user_requests_simple.html', context)

@login_required
@user_passes_test(is_admin)
def complete_request(request, request_id):
    """
    Представление для завершения заявки
    """
    if request.method == 'POST':
        user_request = get_object_or_404(UserRequest, id=request_id)
        user_request.status = 'completed'
        user_request.save()
        
        # Добавляем системное сообщение о завершении заявки
        ChatMessage.objects.create(
            request=user_request,
            sender=request.user,
            message='Заявка завершена администратором',
            is_system=True
        )
        
        messages.success(request, 'Заявка успешно завершена')
        
        # Возвращаем URL для перенаправления
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('admin_requests')
            })
        return redirect('admin_requests')
    
    return JsonResponse({'status': 'error', 'error': 'Метод не поддерживается'}, status=405)

@login_required
@user_passes_test(is_admin)
def load_request_data(request, request_id):
    """
    Представление для загрузки данных заявки через AJAX
    """
    try:
        # Проверяем кэш
        cache_key = f'request_data_{request_id}'
        cached_data = cache.get(cache_key)
        
        # Если есть новые сообщения, игнорируем кэш
        has_unread = request.GET.get('check_unread', 'false') == 'true'
        
        if cached_data and not has_unread:
            return JsonResponse(cached_data)
        
        # Используем select_related для оптимизации запроса
        user_request = get_object_or_404(
            UserRequest.objects.select_related('user'), 
            id=request_id
        )
        
        # Помечаем сообщения пользователя как прочитанные
        unread_count = ChatMessage.objects.filter(
            request=user_request,
            sender__is_staff=False,
            is_read=False
        ).update(is_read=True)  # Используем update для оптимизации
        
        # Получаем все сообщения в чате оптимизированным запросом
        # Ограничиваем количество сообщений для улучшения производительности
        messages_list = user_request.messages.select_related('sender').order_by('-created_at')[:100].order_by('created_at')
        
        # Формируем JSON с данными
        messages_data = []
        for message in messages_list:
            messages_data.append({
                'id': message.id,
                'text': message.message,  # Обратите внимание на изменение ключа с message на text
                'sender_name': message.sender.name,
                'is_from_admin': message.sender.is_staff,  # Обратите внимание на изменение ключа
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_system': message.is_system
            })
        
        data = {
            'id': user_request.id,
            'title': user_request.title,
            'description': user_request.description,
            'status': user_request.status,
            'status_display': user_request.get_status_display(),
            'created_at': user_request.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': user_request.updated_at.strftime('%d.%m.%Y %H:%M'),
            'user': {
                'id': user_request.user.id,
                'name': user_request.user.name,
                'email': user_request.user.email
            },
            'messages': messages_data
        }
        
        # Сохраняем в кэш на 2 минуты
        cache.set(cache_key, data, 120)
        
        return JsonResponse(data)
    except UserRequest.DoesNotExist:
        return JsonResponse({'error': 'Заявка не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_POST
def send_message(request, request_id):
    """
    Представление для отправки сообщения в чат
    """
    try:
        user_request = get_object_or_404(UserRequest, id=request_id)
        
        # Получаем текст сообщения в зависимости от типа запроса
        message_text = ''
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                data = json.loads(request.body.decode('utf-8'))
                message_text = data.get('message', '').strip()
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        else:  # multipart/form-data или application/x-www-form-urlencoded
            message_text = request.POST.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Создаем сообщение
        message = ChatMessage.objects.create(
            request=user_request,
            sender=request.user,
            message=message_text,
            is_read=True  # Сообщения от администратора считаются прочитанными сразу
        )
        
        # Если заявка была в статусе "new", меняем на "in_progress"
        status_changed = False
        system_message = None
        if user_request.status == 'new':
            user_request.status = 'in_progress'
            user_request.save()
            status_changed = True
            
            # Проверяем, нет ли уже системного сообщения о взятии в работу
            system_message_exists = ChatMessage.objects.filter(
                request=user_request,
                is_system=True,
                message='Администратор взял заявку в работу'
            ).exists()
            
            if not system_message_exists:
                # Добавляем системное сообщение о смене статуса
                system_message = ChatMessage.objects.create(
                    request=user_request,
                    sender=request.user,
                    message='Администратор взял заявку в работу',
                    is_system=True
                )
        
        response_data = {
            'status': 'success',
            'message': {
                'id': message.id,
                'message': message.message,
                'sender_name': message.sender.name,
                'is_staff': message.sender.is_staff,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_system': False
            },
            'status_changed': status_changed
        }
        
        # Если было создано системное сообщение, добавляем его в ответ
        if system_message:
            response_data['system_message'] = {
                'id': system_message.id,
                'message': system_message.message,
                'sender_name': system_message.sender.name,
                'is_staff': system_message.sender.is_staff,
                'created_at': system_message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_system': True
            }
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def get_new_messages(request, request_id):
    """
    Представление для получения новых сообщений через AJAX
    """
    try:
        # Получаем запрос и последний полученный ID сообщения
        user_request = get_object_or_404(UserRequest, id=request_id)
        last_message_id = request.GET.get('last_id', 0)
        
        try:
            last_message_id = int(last_message_id)
        except ValueError:
            last_message_id = 0
        
        # Получаем все новые сообщения, которые еще не были получены
        new_messages = ChatMessage.objects.select_related('sender').filter(
            request=user_request,
            id__gt=last_message_id
        ).order_by('created_at')
        
        # Помечаем сообщения от пользователя как прочитанные
        ChatMessage.objects.filter(
            request=user_request,
            sender__is_staff=False,
            is_read=False
        ).update(is_read=True)
        
        # Формируем список сообщений для ответа
        messages_data = []
        for message in new_messages:
            messages_data.append({
                'id': message.id,
                'message': message.message,
                'sender_name': message.sender.name,
                'is_staff': message.sender.is_staff,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_system': message.is_system
            })
        
        return JsonResponse({
            'status': 'success', 
            'messages': messages_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def check_request_updates(request):
    """
    Представление для проверки обновлений заявок (новых непрочитанных сообщений)
    """
    try:
        # Получаем количество непрочитанных сообщений по каждой заявке
        requests_with_messages = UserRequest.objects.filter(
            status__in=['new', 'in_progress']
        ).annotate(
            unread_messages=Count(
                Case(
                    When(messages__is_read=False, messages__sender__is_staff=False, then=1),
                    output_field=IntegerField(),
                )
            )
        ).filter(unread_messages__gt=0).values('id', 'unread_messages')
        
        # Формируем данные для ответа
        updates = {str(r['id']): r['unread_messages'] for r in requests_with_messages}
        
        # Возвращаем количество непрочитанных сообщений для каждой заявки
        return JsonResponse({
            'status': 'success',
            'updates': updates
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def admin_request_detail(request, request_id):
    """
    Представление для просмотра деталей заявки
    """
    # Получаем заявку
    user_request = get_object_or_404(UserRequest.objects.select_related('user'), id=request_id)
    
    # Помечаем сообщения пользователя как прочитанные
    unread_count = ChatMessage.objects.filter(
        request=user_request,
        sender__is_staff=False,
        is_read=False
    ).update(is_read=True)
    
    # Получаем все сообщения в чате оптимизированным запросом
    messages_list = user_request.messages.select_related('sender').order_by('created_at')
    
    context = {
        'request': user_request,
        'messages': messages_list,
        'title': f'Заявка #{user_request.id}: {user_request.title}'
    }
    
    return render(request, 'admin/request_detail.html', context)

@login_required
@user_passes_test(is_admin)
def update_request_status(request, request_id):
    """
    Представление для обновления статуса заявки
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    user_request = get_object_or_404(UserRequest, id=request_id)
    new_status = request.POST.get('status')
    
    if new_status not in dict(UserRequest.STATUS_CHOICES):
        return JsonResponse({'error': 'Неверный статус'}, status=400)
    
    user_request.status = new_status
    user_request.save()
    
    # Добавляем системное сообщение о смене статуса
    status_messages = {
        'in_progress': 'Администратор взял заявку в работу',
        'completed': 'Заявка завершена администратором',
        'rejected': 'Заявка отклонена администратором'
    }
    
    if new_status in status_messages:
        ChatMessage.objects.create(
            request=user_request,
            sender=request.user,
            message=status_messages[new_status],
            is_system=True
        )
    
    # Если это был AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'new_status': new_status,
            'status_display': user_request.get_status_display()
        })
    
    # В противном случае перенаправляем на страницу заявки или список заявок
    if new_status == 'completed':
        messages.success(request, 'Заявка успешно завершена')
        return redirect('admin_requests')
    
    messages.success(request, 'Статус заявки успешно изменен')
    return redirect('admin_request_detail', request_id=request_id) 