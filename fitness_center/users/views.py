from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser, UserRequest, ChatMessage
from workouts.models import Workout, WorkoutRegistration
from trainers.models import Trainer
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField
import os


def register_view(request):
    """
    Представление для регистрации новых пользователей.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Представление для авторизации пользователей.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему!")
                return redirect('home')
            else:
                messages.error(request, "Неверный email или пароль.")
        else:
            # Проверяем, есть ли ошибки в полях формы
            if form.errors:
                # Если есть ошибки не связанные с полями
                if form.non_field_errors():
                    for error in form.non_field_errors():
                        messages.error(request, error)
                # Проверяем ошибки для каждого поля
                for field_name, field_errors in form.errors.items():
                    if field_name != '__all__':  # Игнорируем non-field ошибки, так как они уже обработаны
                        for error in field_errors:
                            messages.error(request, f"{error}")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Представление для выхода пользователя из системы.
    """
    logout(request)
    messages.success(request, "Вы успешно вышли из системы!")
    return redirect('home')


@login_required
def profile_view(request):
    """
    Представление для просмотра профиля пользователя
    """
    # Получаем количество активных записей на тренировки
    active_registrations_count = WorkoutRegistration.objects.filter(
        user=request.user,
        is_active=True
    ).count()
    
    # Получаем количество заявок пользователя
    requests_count = UserRequest.objects.filter(user=request.user).count()
    
    return render(request, 'users/admin_profile.html', {
        'user': request.user,
        'active_tab': 'profile',
        'active_registrations_count': active_registrations_count,
        'requests_count': requests_count
    })


@login_required
def edit_profile_view(request):
    """
    Представление для редактирования профиля пользователя
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('account_profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'user': request.user,
        'active_tab': 'profile'
    })


@login_required
def change_password_view(request):
    """
    Представление для изменения пароля
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('account_profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {
        'form': form,
        'active_tab': 'profile'
    })


@login_required
def schedule_view(request):
    """
    Представление для просмотра расписания тренировок
    """
    today = timezone.now().date()
    
    # Получаем даты на 5 дней, начиная с сегодняшнего дня
    days = [today + timezone.timedelta(days=i) for i in range(5)]
    
    # Получаем часы для расписания (с 9:00 до 21:00)
    hours = list(range(9, 22))
    
    # Получаем параметр trainer_id из запроса, если есть
    trainer_id = request.GET.get('trainer')
    
    # Базовый запрос для предстоящих тренировок на текущую неделю
    base_query = Workout.objects.filter(
        date__gte=days[0],
        date__lte=days[-1]
    )
    
    # Фильтруем тренировки по тренеру, если указан
    if trainer_id:
        base_query = base_query.filter(trainer_id=trainer_id)
    
    # Разделяем тренировки по залам
    small_hall_workouts = base_query.filter(hall='small').select_related('trainer')
    large_hall_workouts = base_query.filter(hall='large').select_related('trainer')
    
    # Получаем записи пользователя на тренировки
    user_registrations = WorkoutRegistration.objects.filter(
        user=request.user,
        is_active=True,
        workout__date__gte=today
    ).select_related('workout__trainer')
    
    # Получаем тренировки, на которые записан пользователь
    registered_workouts = [reg.workout for reg in user_registrations]
    
    # Создаем словарь для быстрого доступа к регистрациям пользователя
    user_registrations_dict = {reg.workout.id: reg for reg in user_registrations}
    
    # Создаем словарь с названиями дней недели на русском
    day_names = {
        0: 'ПН',
        1: 'ВТ',
        2: 'СР',
        3: 'ЧТ',
        4: 'ПТ',
        5: 'СБ',
        6: 'ВС'
    }
    
    # Создаем список с названиями дней для отображения в шапке таблицы
    day_headers = []
    for i, day in enumerate(days):
        weekday = day.weekday()
        is_today = (i == 0)  # Первый день в списке - это сегодня
        day_headers.append({
            'text': f"{day_names[weekday]}, {day.strftime('%d/%m')}",
            'is_today': is_today
        })
    
    return render(request, 'users/schedule.html', {
        'small_hall_workouts': small_hall_workouts,
        'large_hall_workouts': large_hall_workouts,
        'user_registrations': user_registrations,
        'registered_workouts': registered_workouts,
        'user_registrations_dict': user_registrations_dict,
        'today': today,
        'days': days,
        'hours': hours,
        'day_headers': day_headers,
        'active_tab': 'schedule'
    })


@login_required
def register_for_workout(request, workout_id):
    """
    Представление для записи на тренировку
    """
    workout = get_object_or_404(Workout, id=workout_id)
    
    # Проверяем, прошла ли тренировка
    if workout.is_past:
        messages.error(request, 'Нельзя записаться на прошедшую тренировку.')
        return redirect('account_schedule')
    
    # Проверяем, не закрыта ли запись (менее часа до начала)
    if workout.is_registration_closed:
        messages.error(request, 'Запись на тренировку закрыта (менее часа до начала).')
        return redirect('account_schedule')
    
    # Проверяем, есть ли активная запись
    if WorkoutRegistration.objects.filter(user=request.user, workout=workout, is_active=True).exists():
        messages.error(request, 'Вы уже записаны на эту тренировку.')
        return redirect('account_schedule')
    
    # Проверяем, есть ли свободные места
    if workout.is_full:
        messages.error(request, 'К сожалению, все места на эту тренировку заняты.')
        return redirect('account_schedule')
    
    # Проверяем, есть ли неактивная запись, и если есть - активируем её
    existing_registration = WorkoutRegistration.objects.filter(user=request.user, workout=workout, is_active=False).first()
    if existing_registration:
        existing_registration.is_active = True
        existing_registration.save()
    else:
        # Если записи нет совсем - создаём новую
        WorkoutRegistration.objects.create(user=request.user, workout=workout)
    
    messages.success(request, 'Вы успешно записались на тренировку!')
    return redirect('account_schedule')


@login_required
def cancel_workout_registration(request, registration_id):
    """
    Представление для отмены записи на тренировку
    """
    registration = get_object_or_404(WorkoutRegistration, id=registration_id, user=request.user)
    workout = registration.workout
    
    # Проверяем, прошла ли тренировка
    if workout.is_past:
        messages.error(request, 'Нельзя отменить запись на прошедшую тренировку.')
        return redirect('account_schedule')
    
    # Проверяем, не закрыта ли запись (менее часа до начала)
    if workout.is_registration_closed:
        messages.error(request, 'Нельзя отменить запись менее чем за час до начала тренировки.')
        return redirect('account_schedule')
    
    registration.is_active = False
    registration.save()
    messages.success(request, 'Запись на тренировку отменена.')
    return redirect('account_schedule')


@login_required
def trainers_view(request):
    """
    Представление для просмотра списка тренеров
    """
    trainers = Trainer.objects.all()
    today = timezone.now().date()
    
    return render(request, 'users/admin_trainers.html', {
        'trainers': trainers,
        'today': today,
        'active_tab': 'trainers'
    })


@login_required
def requests_view(request):
    """
    Представление для страницы заявок пользователя
    """
    # Обработка создания новой заявки
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        if title and message:
            # Создаем новую заявку
            new_request = UserRequest.objects.create(
                user=request.user,
                title=title,
                description=message,
                status='new'
            )
            
            # Создаем первое сообщение в чате
            ChatMessage.objects.create(
                request=new_request,
                sender=request.user,
                message=message
            )
            
            # Добавляем сообщение об успехе
            messages.success(request, 'Заявка успешно создана!')
            
            # Перенаправляем на страницу с открытой новой заявкой
            return redirect(f'/account/requests/?request_id={new_request.id}')
        else:
            # Если данные неполные, добавляем сообщение об ошибке
            messages.error(request, 'Пожалуйста, заполните все поля формы.')
    
    # Получаем активные заявки (новые и в обработке)
    active_requests = UserRequest.objects.filter(
        user=request.user,
        status__in=['new', 'in_progress']
    ).annotate(
        unread_messages=Count(
            Case(
                When(messages__is_read=False, messages__sender__is_staff=True, then=1),
                output_field=IntegerField(),
            )
        )
    ).order_by('-created_at')
    
    # Получаем завершенные заявки
    completed_requests = UserRequest.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-updated_at')
    
    # Получаем заявку для отображения, если указан request_id
    active_request = None
    request_id = request.GET.get('request_id')
    if request_id:
        try:
            active_request = UserRequest.objects.get(id=request_id, user=request.user)
            # Помечаем сообщения как прочитанные
            ChatMessage.objects.filter(
                request=active_request, 
                sender__is_staff=True, 
                is_read=False
            ).update(is_read=True)
        except UserRequest.DoesNotExist:
            pass
    
    context = {
        'active_requests': active_requests,
        'completed_requests': completed_requests,
        'active_request': active_request,
        'active_tab': 'requests'
    }
    
    return render(request, 'users/requests.html', context)


@login_required
def request_detail(request, request_id):
    """
    Представление для просмотра деталей заявки и чата
    """
    # Получаем заявку
    user_request = get_object_or_404(UserRequest, id=request_id, user=request.user)
    
    # Помечаем сообщения администратора как прочитанные
    user_request.messages.filter(sender__is_staff=True, is_read=False).update(is_read=True)
    
    # Получаем сообщения
    messages_list = user_request.messages.select_related('sender').order_by('created_at')
    
    return render(request, 'users/request_detail.html', {
        'request': user_request,
        'messages': messages_list,
        'active_tab': 'requests'
    })


@login_required
def send_message(request, request_id):
    """
    Отправка сообщения в чат
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    user_request = get_object_or_404(UserRequest, id=request_id, user=request.user)
    
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
    
    return JsonResponse({
        'id': message.id,
        'message': message.message,
        'sender_name': message.sender.name,
        'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
        'is_staff': message.sender.is_staff
    })


@login_required
def get_messages(request, request_id):
    """
    Представление для получения сообщений заявки
    """
    try:
        user_request = get_object_or_404(UserRequest, id=request_id)
        
        # Проверяем, имеет ли пользователь доступ к этой заявке
        if not request.user.is_staff and user_request.user != request.user:
            return JsonResponse({'error': 'У вас нет доступа к этой заявке'}, status=403)
        
        # Получаем сообщения
        messages = ChatMessage.objects.filter(request=user_request).order_by('created_at')
        
        # Форматируем сообщения для ответа
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'message': message.message,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_staff': message.sender.is_staff,
                'sender_name': message.sender.name,
                'is_system': message.is_system,
            })
        
        return JsonResponse({
            'id': user_request.id,
            'title': user_request.title,
            'description': user_request.description,
            'status': user_request.status,
            'status_display': user_request.get_status_display(),
            'created_at': user_request.created_at.strftime('%d.%m.%Y %H:%M'),
            'messages': messages_data,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_new_messages(request, request_id):
    """
    Представление для получения новых сообщений с момента последнего известного ID
    Используется для обновления чата в режиме реального времени
    """
    try:
        user_request = get_object_or_404(UserRequest, id=request_id)
        
        # Проверяем, имеет ли пользователь доступ к этой заявке
        if not request.user.is_staff and user_request.user != request.user:
            return JsonResponse({'error': 'У вас нет доступа к этой заявке'}, status=403)
        
        # Получаем ID последнего известного сообщения
        last_id = request.GET.get('last_id', 0)
        try:
            last_id = int(last_id)
        except ValueError:
            last_id = 0
        
        # Получаем новые сообщения, которые появились после last_id
        new_messages = ChatMessage.objects.filter(
            request=user_request,
            id__gt=last_id
        ).order_by('created_at')
        
        # Если пользователь обычный (не админ), отмечаем сообщения от админа как прочитанные
        if not request.user.is_staff:
            new_messages.filter(is_read=False, sender__is_staff=True).update(is_read=True)
        
        # Форматируем сообщения для ответа
        messages_data = []
        for message in new_messages:
            messages_data.append({
                'id': message.id,
                'message': message.message,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_staff': message.sender.is_staff,
                'sender_name': message.sender.name,
                'is_system': message.is_system,
            })
        
        return JsonResponse({
            'messages': messages_data,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def create_request(request):
    """
    Представление для создания новой заявки пользователя
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if not title or not description:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля')
            return redirect('requests')
        
        # Создаем новую заявку
        user_request = UserRequest.objects.create(
            user=request.user,
            title=title,
            description=description,
            status='new'
        )
        
        # Добавляем системное сообщение о создании заявки
        ChatMessage.objects.create(
            request=user_request,
            sender=request.user,
            message='Заявка создана',
            is_system=True
        )
        
        messages.success(request, 'Заявка успешно создана')
        return redirect('request_detail', request_id=user_request.id)
    
    return render(request, 'users/create_request.html', {
        'active_tab': 'requests'
    })
