from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('products')


class SignInView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('products')

    def form_valid(self, form):
        email = form.cleaned_data.get('username')  # 'username' field holds the email
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect('products')
        else:
            return self.form_invalid(form)


def error_404(request, exception):
    data = {}
    return render(request, 'users/error404.html', data)
