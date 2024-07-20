from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from products.models import Product, Order, Checkout
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


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, transaction_id=order_id, user=request.user)
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])

    # notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    # notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    product_category = [item.product.category for item in order.order_item.all()]

    similar_items = Product.objects.filter(category__in=product_category).exclude(name__in=[item.product for item in order.order_item.all()]).order_by("?")[:2]

    context = {
        "check_out_list": check_out_list,
        "get_cart_total": get_cart_total,
        # "get_cart_items": total_cart_items(request),
        # "notification": notification,
        # "notification_count": notification_count,
        'order': order,
        'similar_items': similar_items,

    }
    return render(request, 'users/order_summary.html', context)


def error_404(request, exception):
    data = {}
    return render(request, 'users/error404.html', data)
