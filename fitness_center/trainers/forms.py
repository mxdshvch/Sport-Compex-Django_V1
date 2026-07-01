from django import forms
from .models import Trainer

class TrainerAdminForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'class': 'quill-editor', 'style': 'min-height: 200px;'}),
        } 