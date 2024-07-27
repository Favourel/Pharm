from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User, Prescription


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )


class UserUpdateForm(forms.ModelForm):
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
    class Meta:
        model = Prescription
        fields = ['full_name', 'email', 'document']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    document = forms.FileField(validators=[validate_file_size])
