from django import forms
from .models import MembershipApplication, Membership


class MembershipApplicationForm(forms.ModelForm):
    """
    Форма для подачи заявки на абонемент.
    """
    class Meta:
        model = MembershipApplication
        fields = ['membership', 'name', 'email', 'phone']
        widgets = {
            'membership': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MembershipApplicationStatusForm(forms.ModelForm):
    """
    Форма для изменения статуса заявки на абонемент администратором.
    """
    class Meta:
        model = MembershipApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class MembershipAdminForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'class': 'quill-editor', 'style': 'min-height: 200px;'}),
        } 