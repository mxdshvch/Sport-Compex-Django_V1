from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей с дополнительными проверками.
    """
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Пароль должен содержать не менее 8 символов.'
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'password1', 'password2')
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать не менее 8 символов.')
        return password


class CustomAuthenticationForm(AuthenticationForm):
    """
    Форма для авторизации пользователей.
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'password')
    
    error_messages = {
        'invalid_login': 'Пожалуйста, введите правильные email адрес и пароль. Оба поля могут быть чувствительны к регистру.',
        'inactive': 'Этот аккаунт неактивен.',
    }


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя
    """
    class Meta:
        model = User
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        } 