from django.shortcuts import render, get_object_or_404, redirect
from .models import Trainer
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def trainers_list(request):
    """
    Список всех тренеров.
    """
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainers_list.html', {'trainers': trainers})


def trainer_detail(request, trainer_id):
    """
    Детальная информация о тренере и его расписание.
    """
    trainer = get_object_or_404(Trainer, id=trainer_id)
    upcoming_workouts = trainer.get_upcoming_workouts()
    return render(request, 'trainers/trainer_detail.html', {
        'trainer': trainer,
        'upcoming_workouts': upcoming_workouts
    })


def trainers_page(request):
    """
    Страница с карточками тренеров в виде слайдера.
    """
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainers_page.html', {'trainers': trainers})


@login_required
def trainer_list(request):
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})


def search_trainers(request):
    """
    AJAX представление для поиска тренеров
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').lower()  # Явно преобразуем запрос в нижний регистр
        trainers = []
        
        if query:
            # Поиск тренеров по имени, специализации или описанию
            # icontains уже означает поиск без учета регистра, но добавим дополнительные меры
            trainer_objects = Trainer.objects.filter(
                Q(name__icontains=query) | 
                Q(specialization__icontains=query) | 
                Q(description__icontains=query)
            )
            
            # Двойная проверка: сначала icontains на уровне базы данных, затем проверка в Python
            # для случаев, когда база данных не полностью поддерживает регистронезависимый поиск
            filtered_trainers = []
            for trainer in trainer_objects:
                if (query in trainer.name.lower() or 
                    query in trainer.specialization.lower() or 
                    query in trainer.description.lower()):
                    filtered_trainers.append(trainer)
            
            # Формируем данные для ответа
            for trainer in filtered_trainers:
                trainers.append({
                    'id': trainer.id,
                    'name': trainer.name,
                    'specialization': trainer.specialization,
                    'photo_url': trainer.photo.url if trainer.photo else None,
                })
        
        return JsonResponse({'trainers': trainers})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_POST
@login_required
def delete_trainer(request, trainer_id):
    """
    Удаление тренера через AJAX
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        trainer = get_object_or_404(Trainer, id=trainer_id)
        trainer_name = trainer.name
        
        # Удаляем тренера
        trainer.delete()
        
        # Возвращаем успешный ответ
        return JsonResponse({
            'status': 'success',
            'message': f'Тренер {trainer_name} успешно удален'
        })
    
    # Если это обычный запрос (не AJAX), делаем обычное удаление
    trainer = get_object_or_404(Trainer, id=trainer_id)
    trainer.delete()
    return redirect('admin:trainers_trainer_changelist')
