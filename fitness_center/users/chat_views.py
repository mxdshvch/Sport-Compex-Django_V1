from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import UserRequest, ChatMessage
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_POST

@login_required
def chat_view(request, request_id):
    """
    Представление для отображения чата конкретной заявки
    """
    user_request = get_object_or_404(UserRequest, id=request_id)
    
    # Проверяем права доступа
    if not request.user.is_staff and request.user != user_request.user:
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('account_requests')
    
    # Помечаем сообщения как прочитанные
    if request.user.is_staff:
        ChatMessage.objects.filter(request=user_request, sender=user_request.user, is_read=False).update(is_read=True)
    else:
        ChatMessage.objects.filter(request=user_request, sender__is_staff=True, is_read=False).update(is_read=True)
    
    # Получаем сообщения с предварительной загрузкой связанных данных
    chat_messages = user_request.messages.select_related('sender').order_by('created_at')
    
    context = {
        'user_request': user_request,
        'messages': chat_messages,
        'is_completed': user_request.status == 'completed'
    }
    
    return render(request, 'users/chat.html', context)

@login_required
@require_POST
def send_message(request, request_id):
    """
    Отправка сообщения в чат
    """
    user_request = get_object_or_404(UserRequest, id=request_id)
    
    # Проверяем, что пользователь имеет право отправлять сообщения
    if not (request.user.is_staff or request.user == user_request.user):
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    # Проверяем, что заявка не завершена
    if user_request.status == 'completed':
        return JsonResponse({'error': 'Заявка завершена'}, status=400)
    
    message_text = request.POST.get('message')
    if not message_text:
        return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
    
    # Создаем новое сообщение
    message = ChatMessage.objects.create(
        request=user_request,
        sender=request.user,
        message=message_text
    )
    
    # Если заявка была новой, переводим её в статус "в обработке"
    if user_request.status == 'new' and request.user.is_staff:
        user_request.status = 'in_progress'
        user_request.save()
    
    return JsonResponse({
        'id': message.id,
        'message': message.message,
        'sender_name': message.sender.name,
        'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
        'is_staff': message.sender.is_staff
    })

@login_required
@require_POST
def complete_request(request, request_id):
    """
    Завершение заявки
    """
    user_request = get_object_or_404(UserRequest, id=request_id)
    
    # Только администратор может завершать заявки
    if not request.user.is_staff:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    # Проверяем, что заявка не завершена
    if user_request.status == 'completed':
        return JsonResponse({'error': 'Заявка уже завершена'}, status=400)
    
    # Завершаем заявку
    user_request.status = 'completed'
    user_request.save()
    
    # Создаем системное сообщение о завершении
    ChatMessage.objects.create(
        request=user_request,
        sender=request.user,
        message='Заявка завершена администратором',
        is_system=True
    )
    
    return JsonResponse({
        'status': 'completed',
        'message': 'Заявка успешно завершена'
    })

@login_required
def get_new_messages(request, request_id):
    """
    Получение новых сообщений
    """
    print(f"[DEBUG] get_new_messages called for request_id={request_id}")
    user_request = get_object_or_404(UserRequest, id=request_id)
    
    # Проверяем, что пользователь имеет право читать сообщения
    if not (request.user.is_staff or request.user == user_request.user):
        print(f"[DEBUG] Access denied for user {request.user.id} to request {request_id}")
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    # Получаем ID последнего известного сообщения и временную метку
    last_id = request.GET.get('last_id', 0)
    last_timestamp = request.GET.get('last_timestamp', None)
    
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0
    
    print(f"[DEBUG] Fetching messages with id > {last_id}")
    
    # Базовый запрос для получения новых сообщений
    query = ChatMessage.objects.filter(request=user_request)
    
    # Фильтруем по ID, если он предоставлен
    if last_id > 0:
        query = query.filter(id__gt=last_id)
    
    # Фильтруем по временной метке, если она предоставлена
    if last_timestamp:
        try:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            
            # Преобразуем строку временной метки в объект datetime
            parsed_timestamp = None
            
            # Пробуем несколько форматов даты
            formats = [
                '%d.%m.%Y %H:%M',  # 01.01.2023 15:30
                '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO формат
                '%Y-%m-%d %H:%M:%S'  # MySQL-подобный формат
            ]
            
            for fmt in formats:
                try:
                    import datetime
                    parsed_timestamp = datetime.datetime.strptime(last_timestamp, fmt)
                    if timezone.is_naive(parsed_timestamp):
                        parsed_timestamp = timezone.make_aware(parsed_timestamp)
                    break
                except ValueError:
                    continue
            
            if parsed_timestamp:
                # Добавляем небольшой запас (1 секунда), чтобы избежать граничных условий
                # из-за различий в точности между клиентом и сервером
                safety_margin = timezone.timedelta(seconds=1)
                parsed_timestamp -= safety_margin
                
                print(f"[DEBUG] Filtering messages after timestamp: {parsed_timestamp}")
                query = query.filter(created_at__gt=parsed_timestamp)
        except Exception as e:
            print(f"[DEBUG] Error parsing timestamp: {e}")
    
    # Получаем новые сообщения и сортируем их по времени создания
    messages = query.order_by('created_at')
    print(f"[DEBUG] Found {messages.count()} new messages")
    
    # Помечаем сообщения как прочитанные
    if request.user.is_staff:
        unread_count = messages.filter(sender__is_staff=False, is_read=False).count()
        messages.filter(sender__is_staff=False, is_read=False).update(is_read=True)
        print(f"[DEBUG] Marked {unread_count} messages as read (staff view)")
    else:
        unread_count = messages.filter(sender__is_staff=True, is_read=False).count()
        messages.filter(sender__is_staff=True, is_read=False).update(is_read=True)
        print(f"[DEBUG] Marked {unread_count} messages as read (user view)")
    
    # Для предотвращения дублирования, проверяем ID сообщений, указанных в параметре already_received
    already_received_ids = []
    already_received_param = request.GET.get('already_received', '')
    if already_received_param:
        try:
            already_received_ids = [int(id) for id in already_received_param.split(',')]
            print(f"[DEBUG] Filtering out already received messages: {already_received_ids}")
        except ValueError:
            print("[DEBUG] Error parsing already_received parameter")
    
    messages_data = []
    for message in messages:
        # Пропускаем сообщения, которые клиент уже получил
        if message.id in already_received_ids:
            print(f"[DEBUG] Skipping already received message ID {message.id}")
            continue
            
        messages_data.append({
            'id': message.id,
            'message': message.message,
            'sender_name': message.sender.name,
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_staff': message.sender.is_staff,
            'is_system': message.is_system
        })
    
    print(f"[DEBUG] Returning {len(messages_data)} messages")
    
    return JsonResponse({
        'messages': messages_data,
        'status': user_request.status
    })

@login_required
def load_request_data(request, request_id):
    """
    Загрузка данных заявки через AJAX
    """
    try:
        # Получаем заявку по ID
        user_request = get_object_or_404(UserRequest, id=request_id)
        
        # Проверяем, имеет ли пользователь доступ к этой заявке
        if not request.user.is_staff and request.user != user_request.user:
            return JsonResponse({
                'error': 'У вас нет доступа к этой заявке'
            }, status=403)
        
        # Получаем все сообщения в чате
        messages_list = user_request.messages.select_related('sender').order_by('created_at')
        
        # Помечаем непрочитанные сообщения как прочитанные
        if request.user.is_staff:
            ChatMessage.objects.filter(
                request=user_request,
                sender__is_staff=False,
                is_read=False
            ).update(is_read=True)
        else:
            ChatMessage.objects.filter(
                request=user_request,
                sender__is_staff=True,
                is_read=False
            ).update(is_read=True)
        
        # Формируем данные для JSON-ответа
        messages_data = []
        for message in messages_list:
            messages_data.append({
                'id': message.id,
                'message': message.message,
                'sender_name': message.sender.name,
                'is_staff': message.sender.is_staff,
                'is_system': message.is_system,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M')
            })
        
        data = {
            'id': user_request.id,
            'title': user_request.title,
            'description': user_request.description,
            'status': user_request.status,
            'status_display': user_request.get_status_display(),
            'created_at': user_request.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': user_request.updated_at.strftime('%d.%m.%Y %H:%M'),
            'messages': messages_data
        }
        
        return JsonResponse(data)
    except UserRequest.DoesNotExist:
        return JsonResponse({'error': 'Заявка не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 