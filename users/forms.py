from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField

from .models import User, Prescription


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'password1', 'password2', 'captcha')


class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()

    class Meta:
        fields = ['email', 'password', 'captcha']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        "name": "email",
        "placeholder": "Enter email address",
        'type': 'email',
        "required": True,
        "id": "email",
        "class": "form-control mb-3"
    }))
    first_name = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "first_name",
        "placeholder": "Enter first name",
        'type': 'text',
        "required": True,
        "id": "first_name",
        "class": "form-control mb-3"
    }))
    address = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "address",
        "placeholder": "Enter address",
        'type': 'text',
        "required": True,
        "id": "address",
        "class": "form-control mb-3"
    }))
    phone_number = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={
        "name": "phone_number",
        "placeholder": "Enter phone_number",
        'type': 'number',
        "required": True,
        "id": "phone_number",
        "class": "form-control mb-3"
    }))
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ["email", "first_name",
                  "address", "phone_number",
                  # "password"
                  ]


def validate_file_size(file):
    max_size_kb = 20
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"The maximum file size that can be uploaded is {max_size_kb}KB")


class PrescriptionUploadForm(forms.ModelForm):
    full_name = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "full_name",
        "placeholder": "Enter full name",
        'type': 'text',
        "required": True,
        "id": "full_name",
        "class": "form-control mb-3"
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        "name": "email",
        "placeholder": "Enter email address",
        'type': 'email',
        "required": True,
        "id": "email",
        "class": "form-control mb-3"
    }))
    captcha = ReCaptchaField()

    class Meta:
        model = Prescription
        fields = ['full_name', 'email', 'document']
        # widgets = {
        #     'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        #
        # }

    document = forms.FileField(validators=[validate_file_size])
