import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Product, Checkout, Order
from users.models import Notification
from .filters import ProductPriceFilter
from .utils import total_cart_items


# Create your views here.


def home_page(request):
    context = {

    }
    return render(request, "products/home.html", context)


@login_required
def products_view(request):
    categories = Category.getAllCategory()
    products = Product.objects.all().order_by("-date_posted")
    maximum_price = Product.objects.all().aggregate(Max("price"))["price__max"]
    half_max_price = maximum_price / 2 if maximum_price else 0

    def get_filtered_products(queryset):
        price_filter = ProductPriceFilter(request.GET, queryset=queryset)
        return price_filter.qs, price_filter

    def get_paginated_products(queryset, page_size=9):
        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    def get_user_data(user):
        notifications = Notification.objects.filter(user=user, is_seen=False).order_by("-id")[:10]
        notification_count = notifications.count()
        check_out_list = Checkout.objects.filter(user=user, complete=False).order_by("-id")
        get_cart_total = sum([item.get_total for item in check_out_list])
        return notifications, notification_count, check_out_list, get_cart_total

    filtered_products, price_filter = get_filtered_products(products)
    paginated_products = get_paginated_products(filtered_products)

    notifications, notification_count, check_out_list, get_cart_total = get_user_data(request.user)

    if request.GET.get('category_name'):
        category_products = Product.getProductByFilter(request.GET['category_name']).order_by('-id')
        filtered_category_products, price_filter = get_filtered_products(category_products)
        paginated_category_products = get_paginated_products(filtered_category_products)
        context = {
            "categories": categories,
            "notification": notifications,
            "notification_count": notification_count,
            "products": paginated_category_products,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,
            "get_cart_items": total_cart_items(request),
            "check_out_list": check_out_list,
            "get_cart_total": get_cart_total,
        }
        return render(request, 'products/product.html', context)

    if request.GET.get('ratings'):
        ratings_query = request.GET.get('ratings')
        ratings_filtered_products = Product.objects.filter(rating_count=ratings_query).distinct()
        filtered_ratings_products, price_filter = get_filtered_products(ratings_filtered_products)
        paginated_ratings_products = get_paginated_products(filtered_ratings_products)
        context = {
            "products": paginated_ratings_products,
            "price_filter": price_filter,
            "categories": categories,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,
            "rating_query": ratings_query,
            "notification": notifications,
            "notification_count": notification_count,
            "check_out_list": check_out_list,
            "get_cart_items": total_cart_items(request)
        }
        return render(request, 'products/product.html', context)

    if request.GET.get('date_posted'):
        date_posted_query = request.GET.get('date_posted')
        date_posted_products = Product.objects.all().order_by(f"-{date_posted_query}")
        filtered_date_posted_products, price_filter = get_filtered_products(date_posted_products)
        paginated_date_posted_products = get_paginated_products(filtered_date_posted_products)
        context = {
            "products": paginated_date_posted_products,
            "categories": categories,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,
            "rating_query": date_posted_query,
            "notification": notifications,
            "notification_count": notification_count,
            "check_out_list": check_out_list,
            "get_cart_items": total_cart_items(request)
        }
        return render(request, 'products/product.html', context)

    context = {
        "notification": notifications,
        "notification_count": notification_count,
        "categories": categories,
        "products": paginated_products,
        "price_filter": price_filter,
        "maximum_price": maximum_price,
        "half_max_price": half_max_price,
        "check_out_list": check_out_list,
        "get_cart_total": get_cart_total,
        "get_cart_items": total_cart_items(request),
    }
    return render(request, "products/product.html", context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    recently_viewed_products = []
    if 'recently_viewed_products' in request.session:
        recently_viewed_ids = request.session['recently_viewed_products']
        recently_viewed_products = Product.objects.filter(pk__in=recently_viewed_ids).exclude(pk=pk)

    try:
        cart_item = Checkout.objects.get(
            user=request.user,
            product=product,
            complete=False,
        )
        cart_item_quantity = cart_item.quantity
    except (Checkout.DoesNotExist):
        cart_item_quantity = 1

    context = {
        "recently_viewed_products": recently_viewed_products,
        "product": product,
        "cart_item_quantity": cart_item_quantity
    }
    return render(request, "products/product_detail.html", context)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if product_id and quantity:
            product = Product.objects.get(id=product_id)

            cart_item, created = Checkout.objects.get_or_create(
                user=request.user,
                product=product,
                complete=False,
            )
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def delete_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    print(Checkout.objects.filter(user=customer, product=product, complete=False))
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product, complete=False).exists():
        print(Checkout.objects.filter(user=customer, product=product, complete=False))
        orderItem.delete()
        messages.success(request, f"'{product.name}' has been removed from your cart")
        return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' doesn't exists in your cart")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def checkout(request):
    notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
    get_cart_total = sum([item.get_total for item in check_out_list])
    # if get_cart_total >= 50000:
    #     get_shipping_fee = 0
    # else:
    #     get_shipping_fee = sum([item.product.shipping_fee for item in check_out_list])
    # form = AddressForm()
    # form_coupon = ApplyCouponForm()
    context = {
        "notification_count": notification_count,
        "notification": notification,
        "items": check_out_list,
        # "form": form,
        # "form_coupon": form_coupon,
        "check_out_list": check_out_list,

        "get_cart_total": get_cart_total,
        # "get_shipping_fee": get_shipping_fee,
        "get_cart_items": total_cart_items(request),
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, "products/checkout.html", context)


@login_required
def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.now().timestamp()
    reference = str(data['ref']['reference'])
    address = data.get('address')
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")

    queryset = []
    for item in check_out_list:
        queryset.append(item.complete == True)
        item.complete = True
        item.save()

    order = Order.objects.create(
        user=request.user,
        transaction_id=transaction_id,
        ordered=True,
        reference=reference,
        address=address,
        order_status="Pending",
    )

    order.order_item.set([item for item in check_out_list])
    order.default_order_item = [str(item) for item in order.order_item.all()]
    order.default_price = sum([item.get_total for item in check_out_list])
    order.save()

    product_queryset = []
    for item in check_out_list:
        product_queryset.append(item.product.product_purchase + item.quantity)
        item.product.product_purchase += item.quantity
        item.product.save()

    notification = Notification.objects.create(
        user=request.user,
        notification_type=1
    )
    notification.orders.set([item for item in check_out_list])
    notification.save()
    # return redirect('order_summary', order_id=order.id)

    return JsonResponse({'message': 'Payment complete!', 'redirect': f'{order.get_absolute_url()}'}, safe=False)
