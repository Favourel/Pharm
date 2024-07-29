import datetime
import os

import cloudinary.uploader
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, FormView

from products.models import Product, Order, Checkout, Category
from products.recommendation import get_recommendations
from products.utils import total_cart_items, throttle
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, PrescriptionUploadForm
from .models import Notification


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('login')

    @method_decorator(throttle(rate=5, period=60))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SignInView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('products')

    @method_decorator(throttle(rate=5, period=60))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data.get('username')  # 'username' field holds the email
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect('products')
        else:
            return self.form_invalid(form)


@login_required
def users_profile(request):
    categories = Category.getAllCategory()
    recommendations = get_recommendations(request.user.id)
    products = [product.name for product in recommendations]

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form = form.save(commit=False)
            form.save()

            messages.success(request, 'Your account has been updated!')
            # return redirect(f"../{request.user}/post/")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        "get_cart_items": total_cart_items(request),
        # "notification": notification,
        # "notification_count": notification_count,
        # 'order': order,
        'form': form,
        'categories': categories,
        "now": datetime.datetime.now().hour,
        "products": products
    }
    return render(request, 'users/profile.html', context)


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, transaction_id=order_id, user=request.user)
    categories = Category.getAllCategory()
    # notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    # notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    product_category = [item.product.category for item in order.order_item.all()]

    similar_items = Product.objects.filter(category__in=product_category).exclude(name__in=[item.product for item in order.order_item.all()]).order_by("?")[:2]

    context = {

        "get_cart_items": total_cart_items(request),
        # "notification": notification,
        # "notification_count": notification_count,
        'order': order,
        'similar_items': similar_items,
        'categories': categories,

    }
    return render(request, 'users/order_summary.html', context)


@login_required
def user_orders(request):
    items = Order.objects.filter(user=request.user)

    return render(request, 'users/partials/user_orders.html',
                  {'items': items})


@login_required
def user_notifications(request):
    """
    user_notifications
    """
    queryset = []
    for i in Notification.objects.filter(user=request.user):
        queryset.append(i.is_seen == True)
        i.is_seen = True
        i.save()

    notification = Notification.objects.filter(user=request.user).order_by("-id")[:10]

    return render(request, 'users/partials/user_notifications.html',
                  {'notification': notification})


@csrf_exempt
def upload_prescription(request):
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return redirect("home")
            return JsonResponse({'success': True, 'message': 'File uploaded successfully.'})
        else:
            errors = dict(form.errors)
        return JsonResponse({'failure': True, 'errors': errors["document"][0]})

    else:
        form = PrescriptionUploadForm()
    return render(request, 'users/partials/user_prescription.html', {'form': form})


def error_404(request, exception):
    data = {}
    return render(request, 'users/error404.html', data)


def handler500(request):
    return render(request, 'users/error404.html', status=500)


def about(request):
    categories = Category.getAllCategory()

    if request.user.is_authenticated:
        get_cart_items = total_cart_items(request)
    else:
        get_cart_items = 0
    return render(request, 'users/about.html', {
        'categories': categories,
        'get_cart_items': get_cart_items,
    })


def disabled_view(request):
    return render(request, 'users/error404.html')
