from django import forms
from .models import WorkoutDirection, TrainingGoal, Workout

class WorkoutDirectionAdminForm(forms.ModelForm):
    """
    Форма для направления тренировок в админке
    """
    goals = forms.ModelMultipleChoiceField(
        queryset=TrainingGoal.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'goals-checkbox-list'}),
        required=False,
        label="Цели тренировки"
    )
    
    class Meta:
        model = WorkoutDirection
        fields = ['name', 'description', 'image', 'goals']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'quill-editor', 'style': 'min-height: 200px;'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'image': 'Изображение'
        }
        help_texts = {
            'description': 'Используйте панель инструментов для форматирования текста: жирный текст, курсив, списки и другие элементы форматирования.',
            'goals': 'Выберите одну или несколько целей, для которых подходит данное направление тренировок.'
        }

class WorkoutDirectionForm(forms.ModelForm):
    """
    Форма для редактирования направления тренировок с улучшенным выбором целей
    """
    goals = forms.ModelMultipleChoiceField(
        queryset=TrainingGoal.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Цели тренировки"
    )
    
    class Meta:
        model = WorkoutDirection
        fields = ['name', 'description', 'image', 'goals']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'image': 'Изображение'
        }
        help_texts = {
            'description': 'Используйте панель инструментов для форматирования текста: жирный текст, курсив, списки и другие элементы форматирования.',
            'goals': 'Выберите одну или несколько целей, для которых подходит данное направление тренировок. Удерживайте Control (или Command на Mac) для выбора нескольких значений.'
        }

class WorkoutAdminForm(forms.ModelForm):
    """
    Форма для тренировки в админке с улучшенным выбором зала
    """
    class Meta:
        model = Workout
        fields = ['title', 'description', 'trainer', 'date', 'time', 'duration', 'max_participants', 'hall']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'hall': forms.RadioSelect(attrs={'class': 'hall-radio-select'})
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'trainer': 'Тренер',
            'date': 'Дата',
            'time': 'Время',
            'duration': 'Длительность (минуты)',
            'max_participants': 'Максимальное количество участников',
            'hall': 'Зал'
        }
        help_texts = {
            'hall': 'Выберите зал, в котором будет проходить тренировка',
            'duration': 'Рекомендуется указывать длительность кратную 15 минутам',
            'max_participants': 'Максимальное количество участников, которые могут записаться на тренировку'
        } 