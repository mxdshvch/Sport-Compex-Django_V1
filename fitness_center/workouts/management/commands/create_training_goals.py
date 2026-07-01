from django.core.management.base import BaseCommand
from workouts.models import TrainingGoal

class Command(BaseCommand):
    help = 'Создает предопределенные цели тренировок'

    def handle(self, *args, **kwargs):
        goals = [
            'Скорректировать вес',
            'Набрать мышечную массу',
            'Обучиться единоборствам',
            'Вовлечь ребенка в спорт',
            'Оставаться в тонусе',
            'Снять стресс',
            'Оставаться молодым',
            'Восстановиться после травмы',
            'Подготовиться к соревнованиям',
            'Занятия вместе с малышом'
        ]
        
        created = 0
        existing = 0
        
        for goal in goals:
            if not TrainingGoal.objects.filter(name=goal).exists():
                TrainingGoal.objects.create(name=goal)
                self.stdout.write(self.style.SUCCESS(f'Создана цель: {goal}'))
                created += 1
            else:
                self.stdout.write(self.style.WARNING(f'Цель уже существует: {goal}'))
                existing += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Готово! Добавлено {created} новых целей, {existing} уже существовали. '
            f'Всего целей в базе данных: {TrainingGoal.objects.count()}'
        )) 