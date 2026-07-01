from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Membership, MembershipApplication
from .forms import MembershipApplicationForm, MembershipApplicationStatusForm
from django.db.models import Q
from django.db import models
from django.core.cache import cache


def memberships_list(request):
    """
    Список всех доступных абонементов.
    """
    memberships = Membership.objects.all()
    return render(request, 'memberships/memberships_list.html', {'memberships': memberships})


def apply_for_membership(request, membership_id=None):
    """
    Подача заявки на абонемент.
    """
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            
            # Если пользователь авторизован, привязываем заявку к нему
            if request.user.is_authenticated:
                application.user = request.user
            
            application.save()
            
            # Отправка уведомления администратору
            subject = 'Новая заявка на абонемент'
            message = f"""
            Поступила новая заявка на абонемент.
            
            Имя: {application.name}
            Email: {application.email}
            Телефон: {application.phone}
            Абонемент: {application.membership.name}
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Отправка на email администратора
                fail_silently=False,
            )
            
            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            
            # Если это AJAX запрос, возвращаем JSON ответ
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'})
            
            return redirect('home')
        else:
            # Если это AJAX запрос, возвращаем ошибки формы
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        # Если указан конкретный абонемент, предзаполняем поле
        initial = {}
        if membership_id:
            membership = get_object_or_404(Membership, id=membership_id)
            initial['membership'] = membership
        
        form = MembershipApplicationForm(initial=initial)
    
    return render(request, 'memberships/apply_for_membership.html', {'form': form})


@login_required
def my_applications(request):
    """
    Просмотр пользователем своих заявок на абонементы.
    """
    applications = MembershipApplication.objects.filter(user=request.user)
    return render(request, 'memberships/my_applications.html', {'applications': applications})


@staff_member_required
def admin_applications_list(request):
    """
    Страница со списком заявок на абонементы для администратора.
    """
    # Получаем все заявки, сортируем по дате создания (новые в начале)
    applications = MembershipApplication.objects.select_related('membership').order_by('-created_at')
    
    # Получаем фильтр по статусу из GET-параметра
    status_filter = request.GET.get('status')
    
    # Применяем фильтр по статусу, если он указан
    if status_filter and status_filter in dict(MembershipApplication.STATUS_CHOICES).keys():
        applications = applications.filter(status=status_filter)
    
    # Поиск по имени, email или телефону
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(phone__icontains=search_query)
        )
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': MembershipApplication.STATUS_CHOICES
    }
    
    # Проверяем, является ли запрос AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'memberships/admin_applications_list_partial.html', context)
    
    return render(request, 'memberships/admin_applications_list.html', context)


@staff_member_required
def admin_application_update(request, application_id):
    """
    Обновление статуса заявки администратором.
    """
    application = get_object_or_404(MembershipApplication, id=application_id)
    
    if request.method == 'POST':
        form = MembershipApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            
            # Отправка уведомления пользователю о изменении статуса
            subject = 'Обновление статуса заявки на абонемент'
            status_text = dict(MembershipApplication.STATUS_CHOICES).get(application.status)
            message = f"""
            Уважаемый(ая) {application.name}!
            
            Статус вашей заявки на абонемент "{application.membership.name}" был изменен на "{status_text}".
            
            С уважением, администрация фитнес-центра.
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Статус заявки успешно обновлен на "{status_text}".')
            return redirect('admin_applications_list')
    else:
        form = MembershipApplicationStatusForm(instance=application)
    
    return render(request, 'memberships/admin_application_update.html', {
        'form': form,
        'application': application
    })


@staff_member_required
def admin_application_update_status(request, application_id):
    """
    AJAX-обновление статуса заявки администратором.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        application = get_object_or_404(MembershipApplication, id=application_id)
        new_status = request.POST.get('status')
        
        # Проверяем, что статус допустимый
        if new_status not in dict(MembershipApplication.STATUS_CHOICES).keys():
            return JsonResponse({'error': 'Недопустимый статус'}, status=400)
        
        # Обновляем статус
        old_status = application.status
        application.status = new_status
        application.save()
        
        # Получаем текстовое представление статуса
        status_text = dict(MembershipApplication.STATUS_CHOICES).get(new_status)
        
        # Отправка уведомления пользователю о изменении статуса
        if old_status != new_status:
            subject = 'Обновление статуса заявки на абонемент'
            message = f"""
            Уважаемый(ая) {application.name}!
            
            Статус вашей заявки на абонемент "{application.membership.name}" был изменен на "{status_text}".
            
            С уважением, администрация фитнес-центра.
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=False,
            )
        
        return JsonResponse({
            'success': True, 
            'status': new_status,
            'status_text': status_text
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def submit_membership_application(request):
    """
    Обработка AJAX-запросов для отправки заявок на абонементы.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Получаем данные из запроса
        membership_id = request.POST.get('membership_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message', '')
        
        # Проверка обязательных полей
        errors = {}
        if not name:
            errors['name'] = 'Это поле обязательно для заполнения'
        if not phone:
            errors['phone'] = 'Это поле обязательно для заполнения'
        if not membership_id:
            errors['membership_id'] = 'Не указан абонемент'
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        try:
            # Находим абонемент по ID
            membership = Membership.objects.get(id=membership_id)
            
            # Создаем новую заявку
            application = MembershipApplication(
                membership=membership,
                name=name,
                email=email,
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
            Email: {email}
            Телефон: {phone}
            Абонемент: {membership.name}
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
            
        except Membership.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'errors': {'membership_id': 'Указанный абонемент не существует'}
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'errors': {'general': f'Произошла ошибка при обработке заявки: {str(e)}'}
            })
    
    return JsonResponse({'success': False, 'message': 'Недопустимый запрос'}, status=400)


@staff_member_required
def admin_application_search(request):
    """
    AJAX-поиск заявок на абонементы для административной панели.
    Оптимизированная версия для быстрой работы.
    """
    try:
        # Получаем параметры запроса
        search_query = request.GET.get('query', '')
        status_filter = request.GET.get('status', '')
        
        # Используем кэш для результатов поиска
        cache_key = f'membership_search_{search_query}_{status_filter}'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return JsonResponse(cached_results)
        
        # Базовый queryset с оптимизацией
        applications = MembershipApplication.objects.select_related('membership').only(
            'id', 'name', 'email', 'phone', 'status', 'created_at', 
            'membership__name', 'membership__price'
        )
        
        # Применяем фильтр по статусу, если он указан
        if status_filter and status_filter in dict(MembershipApplication.STATUS_CHOICES).keys():
            applications = applications.filter(status=status_filter)
        
        # Поиск по имени, email или телефону
        if search_query:
            applications = applications.filter(
                models.Q(name__icontains=search_query) | 
                models.Q(email__icontains=search_query) | 
                models.Q(phone__icontains=search_query)
            )
        
        # Ограничиваем количество результатов для ускорения
        applications = applications[:50]
        
        # Формируем результаты поиска
        results = []
        for app in applications:
            membership_name = app.membership.name if app.membership else "Неизвестный абонемент"
            membership_price = float(app.membership.price) if app.membership else 0.0
            
            results.append({
                'id': app.id,
                'name': app.name,
                'email': app.email or "",
                'phone': app.phone,
                'membership': {
                    'name': membership_name,
                    'price': membership_price
                },
                'status': app.status,
                'status_display': dict(MembershipApplication.STATUS_CHOICES).get(app.status),
                'created_at': app.created_at.strftime('%d %B %Y г. %H:%M')
            })
        
        # Формируем ответ
        response_data = {
            'success': True,
            'count': len(results),
            'applications': results
        }
        
        # Кэшируем результаты на 1 минуту
        cache.set(cache_key, response_data, 60)
        
        return JsonResponse(response_data)
    except Exception as e:
        import traceback
        print(f"Ошибка в admin_application_search: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
