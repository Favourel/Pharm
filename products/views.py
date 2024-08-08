import json
import os
import uuid
from datetime import datetime
from statistics import mean

import requests
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Q, Sum
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from haystack.query import SearchQuerySet
from rest_framework import mixins, viewsets

from .forms import CheckoutForm, ReviewForm
from .models import Category, Product, Checkout, Order, ProductReview, Payment
from users.models import Notification
from .filters import ProductPriceFilter
from .serializers import ProductSearchSerializer
from .utils import total_cart_items


# Create your views here.


def home_page(request):
    if request.user.is_authenticated:
        get_cart_items = total_cart_items(request)
    else:
        get_cart_items = 0
    categories = Category.getAllCategory()
    context = {
        "categories": categories,
        "get_cart_items": get_cart_items,
    }
    return render(request, "products/home.html", context)


def products_view(request):
    categories = Category.getAllCategory()
    products = Product.objects.all().order_by("-date_posted")
    maximum_price = Product.objects.all().aggregate(Max("price"))
    half_max_price = maximum_price["price__max"] / 2

    def get_filtered_products(queryset):
        price_filter = ProductPriceFilter(request.GET, queryset=queryset)
        return price_filter.qs, price_filter

    def get_paginated_products(queryset, page_size=20):
        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    def get_user_data(user):
        if request.user.is_authenticated:
            notifications = Notification.objects.filter(user=user, is_seen=False).order_by("-id")[:10]
            notification_count = notifications.count()
            check_out_list = Checkout.objects.filter(user=user, complete=False).order_by("-id")
            get_cart_total = sum([item.get_total for item in check_out_list])

            return notifications, notification_count, check_out_list, get_cart_total

    filtered_products, price_filter = get_filtered_products(products)
    paginated_products = get_paginated_products(filtered_products)

    if request.user.is_authenticated:
        get_cart_items = total_cart_items(request)
        notifications, notification_count, check_out_list, get_cart_total = get_user_data(request.user)
    else:
        get_cart_items = 0

    if request.GET.get('category_name'):
        category_products = Product.getProductByFilter(request.GET['category_name']).order_by('-id')
        filtered_category_products, price_filter = get_filtered_products(category_products)
        paginated_category_products = get_paginated_products(filtered_category_products)
        if request.user.is_authenticated:
            get_cart_items = total_cart_items(request)
        else:
            get_cart_items = 0
        context = {
            "categories": categories,

            "products": paginated_category_products,
            "maximum_price": maximum_price,
            "half_max_price": half_max_price,
            "get_cart_items": get_cart_items,

        }
        return render(request, 'products/product.html', context)

    context = {
        # "notification": notifications,
        # "notification_count": notification_count,
        "categories": categories,
        "products": paginated_products,
        "price_filter": price_filter,
        "maximum_price": maximum_price,
        "half_max_price": half_max_price,
        # "check_out_list": check_out_list,
        # "get_cart_total": get_cart_total,
        "get_cart_items": get_cart_items

    }
    return render(request, "products/product.html", context)


def filter_products(request):
    sort_by = request.GET.get('sort_by', 'product-purchase')
    if sort_by == 'product-purchase':
        products = Product.objects.all().order_by('-product_purchase')
    elif sort_by == 'created-desc':
        products = Product.objects.all().order_by('-date_posted')
    elif sort_by == 'price-asc':
        products = Product.objects.all().order_by('price')
    elif sort_by == 'price-desc':
        products = Product.objects.all().order_by('-price')
    else:
        products = Product.objects.all()

    return render(request, 'products/partials/product-list.html', {'products': products})


# @login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.getAllCategory()

    recently_viewed_products = []
    if 'recently_viewed_products' in request.session:
        recently_viewed_ids = request.session['recently_viewed_products']
        recently_viewed_products = Product.objects.filter(pk__in=recently_viewed_ids).exclude(pk=pk)
    if request.user.is_authenticated:
        get_cart_items = total_cart_items(request)
        try:
            cart_item = Checkout.objects.get(
                user=request.user,
                product=product,
                complete=False,
            )
            cart_item_quantity = cart_item.quantity
        except (Checkout.DoesNotExist):
            cart_item_quantity = 1
    else:
        cart_item_quantity = 0
        get_cart_items = 0

    context = {
        "recently_viewed_products": recently_viewed_products,
        "product": product,
        "categories": categories,
        "cart_item_quantity": cart_item_quantity,
        "get_cart_items": get_cart_items,
    }
    return render(request, "products/product_detail.html", context)


def product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            ratings = [i.rating for i in product.productreview_set.all()]
            product.rating_count = round(mean(ratings))
            product.save()

            # if request.htmx:
            #     reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
            #     return render(request, 'products/partials/review_list.html', {'product': product, 'reviews': reviews})
            #
            return redirect('product-detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'products/partials/review_form.html', {'form': form, 'product': product})


def search_view(request):
    # notification = Notification.objects.filter(user=request.user, is_seen=False).order_by("-id")[:10]
    # notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    if request.method == "GET":
        # query = request.GET.get('q')
        query = request.GET.get('q')
        submitbutton = request.GET.get('submit')
        if query is not None:

            # search_results = SearchQuerySet().filter(content=query)
            # print(search_results)
            # context = {'query': query, 'search_results': search_results}

            lookups_product = (Q(name__icontains=query) | Q(description__icontains=query)
                               | Q(category__name__icontains=query))
            result_product = Product.objects.filter(lookups_product).distinct()
            # check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")
            # get_cart_total = sum([item.get_total for item in check_out_list])

            categories = Category.getAllCategory()

            # maximum_price = Product.objects.filter(lookups_product).distinct().aggregate(Max("price"))
            # half_max_price = maximum_price["price__max"] / 2

            price_filter = ProductPriceFilter(request.GET, queryset=result_product)
            result_product = price_filter.qs

            if request.user.is_authenticated:
                get_cart_items = total_cart_items(request)
            else:
                get_cart_items = 0

            context = {
                # "check_out_list": check_out_list,
                # "get_cart_total": get_cart_total,
                'submitbutton': submitbutton,
                # 'half_max_price': half_max_price,
                # "maximum_price": maximum_price,

                "products": result_product,
                "categories": categories,
                "query": query,
                # "notification_count": notification_count,
                # "notification": notification,
                "get_cart_items": get_cart_items
            }
            return render(request, "products/product.html", context)
        else:
            context = {
                'submitbutton': submitbutton,
                # "notification_count": notification_count,
                # "notification": notification,
                "get_cart_items": total_cart_items(request)
            }
            return render(request, 'products/product.html', context)
    return render(request, "products/product.html", {})


class ProductSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSearchSerializer

    def get_queryset(self, *args, **kwargs):
        params = self.request.query_params
        query = SearchQuerySet().all()
        keywords = params.get('q')
        if keywords:
            query = query.filter(Q(name=keywords) | Q(description=keywords))

            print(keywords)
        print(query)
        print(query.load_all())
        print([i for i in query])

        return query


def product_search_page(request):
    return render(request, 'products/product_search.html')


def haystack_search(request):
    products = SearchQuerySet().autocomplete(content_auto=request.POST.get("search_text", ""))
    if request.user.is_authenticated:
        get_cart_items = total_cart_items(request)
    else:
        get_cart_items = 0

    return render(request, "products/product.html", {
        "products": products, "get_cart_items": get_cart_items})


@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity')
            print(quantity)

            # Ensure quantity is at least 1
            if int(quantity) < 1:
                return JsonResponse({'success': False, 'error': 'Quantity must be at least 1'}, status=400)

            if product_id and quantity:
                product = get_object_or_404(Product, id=product_id)

                cart_item, created = Checkout.objects.get_or_create(
                    user=request.user,
                    product=product,
                    complete=False,
                )
                cart_item.quantity = quantity
                cart_item.save()

                total_quantity = Checkout.objects.filter(user=request.user, complete=False).aggregate(Sum('quantity'))[
                                     'quantity__sum'] or 0

                return JsonResponse({'success': True, 'message': f'{product.name} (x{quantity}) added to cart.',
                                     "total_quantity": total_quantity})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid data'})
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Request body: {request.body}")
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def add_to_checkout(request, pk):
    user = request.user
    product = get_object_or_404(Product, pk=pk)
    # checkout_list = Checkout.objects.filter(user=user, complete=False)

    create_object, created = Checkout.objects.get_or_create(
        user=user,
        product=product,
        complete=False,
    )
    create_object.quantity = (create_object.quantity + 1)
    create_object.price = (create_object.quantity * create_object.product.price)
    create_object.save()
    if create_object.quantity > 1:
        messages.success(request, f'"{product}" quantity has been updated!')
    else:
        messages.success(request, f'"{product}" has been added to your cart!')
    return redirect("checkout")


@login_required
def remove_from_checkout(request, pk):
    customer = request.user
    product = get_object_or_404(Product, pk=pk)
    orderItem, created = Checkout.objects.get_or_create(user=customer, product=product, complete=False)
    if Checkout.objects.filter(user=customer, product=product).exists():
        if orderItem.quantity <= 0:
            orderItem.delete()
            messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
            return redirect("checkout")
        if orderItem.quantity >= 1:
            orderItem.quantity = (orderItem.quantity - 1)
            orderItem.price = (orderItem.quantity * orderItem.product.price)
            orderItem.save()
            messages.success(request, f"'{product.name}' quantity has been reduced from your cart/checkout")
            return redirect("checkout")
    else:
        messages.success(request, f"'{product.name}' has been removed from your cart/checkout")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return render(request, 'products/checkout.html', {})


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

    initial_data = {'address': request.user.address} if request.user.address else {}
    form = CheckoutForm(initial=initial_data)

    categories = Category.getAllCategory()

    context = {
        "notification_count": notification_count,
        "notification": notification,
        "items": check_out_list,
        "form": form,
        "categories": categories,
        # "form_coupon": form_coupon,
        "check_out_list": check_out_list,

        "get_cart_total": get_cart_total,
        # "get_shipping_fee": get_shipping_fee,
        "get_cart_items": total_cart_items(request),
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        "ALGOLIA_APP_ID": os.environ.get("ALGOLIA_APP_ID"),
        "ALGOLIA_API_KEY": os.environ.get("ALGOLIA_API_KEY")
    }
    return render(request, "products/checkout.html", context)


@csrf_exempt
@login_required
def process_order(request, reference):
    payment = Payment.objects.get(reference=reference)
    data = {
        'ref': {'reference': reference},
        'address': payment.address
    }
    transaction_id = datetime.now().timestamp()
    reference = str(data['ref']['reference'])

    # data = json.loads(request.body)
    # transaction_id = datetime.now().timestamp()
    # reference = str(data['ref']['reference'])
    address = data.get('address')

    # address = data.get('address')
    check_out_list = Checkout.objects.filter(user=request.user, complete=False).order_by("-id")

    for item in check_out_list:
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

    # Update user's address
    request.user.address = address
    request.user.save()

    for item in check_out_list:
        item.product.product_purchase += item.quantity
        item.product.save()

    notification = Notification.objects.create(
        user=request.user,
        notification_type=2
    )
    notification.orders.set([item for item in check_out_list])
    notification.save()

    return redirect(order.get_absolute_url())


@csrf_exempt
@login_required
def initialize_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = int(float(data['amount'])) * 100  # Convert to kobo
        email = request.user.email
        address = data['address']
        reference = str(uuid.uuid4())  # Generate a unique reference
        callback_url = request.build_absolute_uri(
            reverse('verify_payment', args=[reference])
        )
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": amount,
            "callback_url": callback_url,
            "reference": reference
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            Payment.objects.create(
                user=request.user,
                amount=amount / 100,  # Convert back to naira
                reference=reference,
                address=address
            )
            return JsonResponse({'redirect_url': response_data['data']['authorization_url']})
        else:
            return JsonResponse(response.json(), status=response.status_code)

    return render(request, 'products/initialize_payment.html')


@csrf_exempt
@login_required
def verify_payment(request, reference):
    if reference:
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['data']['status'] == 'success':
                payment = Payment.objects.get(reference=reference)
                payment.status = 'completed'
                payment.save()

                # Call process_order here
                return process_order(request, reference)
            else:
                return render(request, 'products/payment_failed.html', {'response': response_data})
        else:
            return JsonResponse(response.json(), status=response.status_code)
    else:
        return HttpResponse('Reference not found', status=400)


@csrf_exempt
@login_required
def paystack_webhook(request):
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload'}, status=400)

        if event['event'] == 'charge.success':
            data = event['data']
            reference = data['reference']
            try:
                payment = Payment.objects.get(reference=reference)
                payment.status = 'completed'
                payment.save()
            except Payment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)

            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Unhandled event'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def product_detail_modal(request, pk):
    product = get_object_or_404(Product, id=pk)
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
        "cart_item_quantity": cart_item_quantity,
        "product": product
    }

    return render(request, 'products/partials/product-detail.html',
                  context)


