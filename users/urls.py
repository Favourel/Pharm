from django.urls import path
from . import views as user_view
from users.middlewares.auth import LogoutCheckMiddleware
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('signup/', user_view.SignUpView.as_view(), name='signup'),
    # path('login/', LogoutCheckMiddleware(user_view.SignInView.as_view()), name='login'),
    path("login/", LogoutCheckMiddleware(auth_view.LoginView.as_view(template_name="users/login.html")), name="login"),

    path("logout/", auth_view.LogoutView.as_view(), name="logout"),

    # path("update_notification/", user_view.update_notification, name="update_notification"),
    path("users/profile/", user_view.users_profile, name="users_profile"),
    path("users/orders/", user_view.user_orders, name="user_orders"),
    path("order-summary/<str:order_id>/", user_view.order_summary, name="order_summary"),
    path("users/user_notifications/", user_view.user_notifications, name="user_notifications"),

    path('upload_prescription/', user_view.upload_prescription, name='upload_prescription'),

    path("about/", user_view.about, name="about"),

    path("password/reset/", auth_view.PasswordResetView.as_view(
        template_name='users/password_reset.html'), name='password_reset'),
    path("password/reset/done/", auth_view.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/key/<uidb64>/<token>/',
         auth_view.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password/reset/key/done/',
         auth_view.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password/change/', user_view.disabled_view, name='account_change_password'),
    path('email/', user_view.disabled_view, name='account_email'),
    path('inactive/', user_view.disabled_view, name='account_inactive'),
    path('reauthenticate/', user_view.disabled_view, name='account_inactive'),
    path('confirm-email/', user_view.disabled_view, name='account_email_verification_sent'),
    path('3rdparty/', user_view.disabled_view),

]
