from django.urls import path
from . import views as user_view
from users.middlewares.auth import LogoutCheckMiddleware


urlpatterns = [
    path('signup/', user_view.SignUpView.as_view(), name='signup'),
    path('login/', LogoutCheckMiddleware(user_view.SignInView.as_view()), name='login'),

    # path("update_notification/", user_view.update_notification, name="update_notification"),
    path("order-summary/<str:order_id>/", user_view.order_summary, name="order_summary"),
    # path("user/order/", user_view.user_orders, name="user_orders"),

    # path("offline/", user_view.offline, name="offline"),
]
