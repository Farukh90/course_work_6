from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import UserCreateView, email_verification, password_reset_request

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path(
        "email-confirmation/<str:token>/", email_verification, name="email_confirmation"
    ),
    path("password-reset/", password_reset_request, name="password_reset"),
]
