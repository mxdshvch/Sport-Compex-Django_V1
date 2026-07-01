from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import WorkoutDirection, Workout, TrainingGoal
from django.core.mail import send_mail
from django.conf import settings
from memberships.models import Membership
from memberships.forms import MembershipApplicationForm
from trainers.models import Trainer
from django.http import JsonResponse
import datetime


def home_view(request):
    """
    Главная страница сайта.
    """
    # Получаем 3 абонемента для отображения на главной странице
    memberships = Membership.objects.all()[:3]
    
    # Получаем всех тренеров для слайдера
    trainers = Trainer.objects.all()
    
    # Получаем направления тренировок (все направления)
    directions = WorkoutDirection.objects.all()
    
    # Получаем цели тренировок
    training_goals = TrainingGoal.objects.all()
    
    application_form = MembershipApplicationForm()
    
    context = {
        'memberships': memberships,
        'trainers': trainers,
        'directions': directions,
        'training_goals': training_goals,
        'application_form': application_form,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    return render(request, 'workouts/home.html', context)


def directions_list(request):
    """
    Список всех направлений тренировок с возможностью фильтрации по целям.
    """
    goals = TrainingGoal.objects.all()
    goals_param = request.GET.get('goals')
    goal_param = request.GET.get('goal')  # Добавляем поддержку единичного параметра goal
    
    directions = WorkoutDirection.objects.all()
    
    if goals_param:
        goal_ids = goals_param.split(',')
        # Фильтрация направлений, соответствующих хотя бы одной из выбранных целей
        directions = directions.filter(goals__id__in=goal_ids).distinct()
    elif goal_param:
        # Фильтрация по названию цели
        goal = TrainingGoal.objects.filter(name__iexact=goal_param).first()
        if goal:
            directions = directions.filter(goals=goal)
        else:
            # Попробуем сопоставить со значением атрибута data-goal в шаблоне
            goal_mapping = {
                'weight-loss': 'скорректировать вес',
                'muscle-gain': 'набрать мышечную массу',
                'martial-arts': 'обучиться единоборствам',
                'fitness': 'оставаться в тонусе',
                'stress-relief': 'снять стресс',
                'anti-aging': 'оставаться молодым',
                'rehabilitation': 'восстановиться после травмы',
                'competition': 'подготовиться к соревнованиям',
                'family': 'занятия вместе с малышом'
            }
            
            goal_name = goal_mapping.get(goal_param, '').lower()
            if goal_name:
                goal = TrainingGoal.objects.filter(name__icontains=goal_name).first()
                if goal:
                    directions = directions.filter(goals=goal)
    
    selected_goals = []
    if goals_param:
        selected_goals = goals_param.split(',')
    elif goal_param:
        selected_goals = [goal_param]
    
    return render(request, 'workouts/directions_list.html', {
        'directions': directions,
        'goals': goals,
        'selected_goals': selected_goals
    })


def direction_detail(request, direction_id):
    """
    Детальная информация о направлении тренировок.
    """
    direction = get_object_or_404(WorkoutDirection, id=direction_id)
    return render(request, 'workouts/direction_detail.html', {'direction': direction})


def schedule(request):
    """
    Расписание тренировок с возможностью фильтрации.
    """
    today = timezone.now().date()
    
    # Фильтры
    direction_id = request.GET.get('direction')
    trainer_id = request.GET.get('trainer')
    date_param = request.GET.get('date')
    
    workouts = Workout.objects.filter(date__gte=today)
    
    if direction_id:
        workouts = workouts.filter(direction_id=direction_id)
    if trainer_id:
        workouts = workouts.filter(trainer_id=trainer_id)
    if date_param:
        workouts = workouts.filter(date=date_param)
        selected_date = datetime.datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        selected_date = today
        
    # Отладочная информация
    print(f"Total workouts: {workouts.count()}")
    for workout in workouts[:3]:  # Выводим информацию о первых 3 тренировках
        print(f"Workout: {workout.direction.name}, {workout.date}, {workout.start_time}")
    
    # Вычисляем даты для недельного расписания
    # Найдем понедельник текущей недели
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    week_dates = []
    day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    
    for i in range(7):
        day_date = start_of_week + datetime.timedelta(days=i)
        week_dates.append({
            'date': day_date,
            'date_str': day_date.isoformat(),  # ISO формат для точного сравнения
            'formatted': day_date.strftime('%d.%m'),
            'name': day_names[i],
            'is_today': day_date == timezone.now().date(),
            'day_num': str(i + 1)  # день недели в формате Django (1-7)
        })
    
    directions = WorkoutDirection.objects.all()
    # Импортируем тренеров из приложения trainers
    trainers = Trainer.objects.all()
    
    # Создаем список часов для расписания (с 7:00 до 22:00)
    schedule_hours = [i for i in range(7, 23)]
    
    return render(request, 'workouts/schedule.html', {
        'workouts': workouts,
        'directions': directions,
        'trainers': trainers,
        'current_direction': direction_id,
        'current_trainer': trainer_id,
        'current_date': date_param,
        'hours': schedule_hours,
        'week_dates': week_dates,
        'current_weekday': str(timezone.now().weekday() + 1)  # Текущий день недели (1-7)
    })


@login_required
def book_workout(request, workout_id):
    """
    Запись пользователя на тренировку.
    """
    workout = get_object_or_404(Workout, id=workout_id)
    user = request.user
    
    # Проверка, что тренировка еще не прошла
    if workout.date < timezone.now().date() or \
       (workout.date == timezone.now().date() and workout.start_time < timezone.now().time()):
        messages.error(request, "Невозможно записаться на прошедшую тренировку.")
        return redirect('account_schedule')
    
    # Проверка, что тренировка не заполнена
    if workout.is_full:
        messages.error(request, "К сожалению, все места на эту тренировку заняты.")
        return redirect('account_schedule')
    
    # Проверка, что пользователь еще не записан на эту тренировку
    if user in workout.participants.all():
        messages.warning(request, "Вы уже записаны на эту тренировку.")
        return redirect('account_schedule')
    
    # Запись на тренировку
    workout.participants.add(user)
    
    # Отправка уведомления по email
    send_mail(
        'Запись на тренировку',
        f'Вы успешно записались на тренировку: {workout}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )
    
    messages.success(request, "Вы успешно записались на тренировку!")
    return redirect('account_schedule')


@login_required
def cancel_booking(request, workout_id):
    """
    Отмена записи на тренировку.
    """
    workout = get_object_or_404(Workout, id=workout_id)
    
    # Проверяем, что пользователь записан на тренировку
    if request.user not in workout.participants.all():
        messages.error(request, 'Вы не записаны на эту тренировку')
        return redirect('account_schedule')
    
    workout.participants.remove(request.user)
    messages.success(request, 'Вы успешно отменили запись на тренировку')
    return redirect('account_schedule')


def submit_application(request):
    """
    Обработка AJAX-запросов для отправки заявок на абонементы.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Получаем данные из запроса
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        service = request.POST.get('service', 'Приобретение абонемента')
        message = request.POST.get('message', '')
        
        # Проверка обязательных полей
        errors = {}
        if not name:
            errors['membershipApplicantName'] = 'Пожалуйста, укажите ваше ФИО'
        if not phone:
            errors['membershipApplicantPhone'] = 'Пожалуйста, укажите ваш телефон'
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        try:
            # Создаем новую заявку (запись в базе данных)
            # Здесь используем произвольный абонемент, так как конкретный абонемент не указан
            default_membership = Membership.objects.first()
            if default_membership:
                from memberships.models import MembershipApplication
                
                application = MembershipApplication(
                    membership=default_membership,
                    name=name,
                    phone=phone
                )
                
                # Если пользователь авторизован, привязываем заявку к нему
                if request.user.is_authenticated:
                    application.user = request.user
                
                application.save()
            
            # Отправка уведомления администратору
            subject = 'Новая заявка на абонемент'
            email_message = f"""
            Поступила новая заявка на абонемент.
            
            Имя: {name}
            Телефон: {phone}
            Услуга: {service}
            Комментарий: {message}
            """
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Отправка на email администратора
                    fail_silently=True,
                )
            except Exception as e:
                # В случае ошибки отправки, просто логируем её, но не прерываем процесс
                print(f"Ошибка отправки email: {e}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'errors': {'general': f'Произошла ошибка при обработке заявки: {str(e)}'}
            })
    
    return JsonResponse({'success': False, 'message': 'Недопустимый запрос'}, status=400)


def trainers_carousel(request):
    """
    Страница с карточками тренеров.
    """
    trainers = Trainer.objects.all()
    # Добавляем направления тренировок
    directions = WorkoutDirection.objects.all()
    
    return render(request, 'workouts/trainers_slider.html', {
        'trainers': trainers,
        'directions': directions,
    })
