from django.shortcuts import redirect, get_object_or_404


def LogoutCheckMiddleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            return redirect("products")
        return get_response(request)
    return middleware
