from django.urls import path
from . import views as user_view
from users.middlewares.auth import LogoutCheckMiddleware


urlpatterns = [
    path('signup/', user_view.SignUpView.as_view(), name='signup'),
    path('login/', LogoutCheckMiddleware(user_view.SignInView.as_view()), name='login'),
]
