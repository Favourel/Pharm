from products.models import Checkout
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import time


def total_cart_items(request):
    check_out_list = Checkout.objects.filter(user=request.user, complete=False)
    get_cart_items = sum([item.quantity for item in check_out_list])
    return get_cart_items


def throttle(rate, period):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            key = f"throttle_{request.META.get('REMOTE_ADDR')}_{view_func.__name__}"
            history = cache.get(key, [])
            now = time.time()
            history = [timestamp for timestamp in history if now - timestamp < period]

            if len(history) >= rate:
                return JsonResponse({"error": "Too many requests"}, status=429)

            history.append(now)
            cache.set(key, history, period)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
