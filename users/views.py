import secrets
import random
import string
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from users.forms import UserRegisterForm, PasswordResetForm
from users.models import User
from config.settings import EMAIL_HOST_USER


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirmation/{token}/"
        try:
            send_mail(
                subject="Подтверждение почты",
                message=f"Привет! , перейди по ссылке для подтверждения почты {url}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
        except Exception as e:
            user.delete()
            messages.error(
                self.request, "Ошибка при отправке письма. Попробуйте еще раз."
            )
            return redirect("users:register")
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None
    user.save()
    return redirect(reverse("users:login"))


def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                new_password = generate_password()
                user.password = make_password(new_password)
                user.save()
                try:
                    send_mail(
                        "Восстановление пароля",
                        f"Ваш новый пароль: {new_password}",
                        EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(
                        request, f"Новый пароль отправлен на почтовый ящик {user.email}"
                    )
                except Exception as e:
                    messages.error(
                        request, "Ошибка при отправке письма. Попробуйте еще раз."
                    )
                return redirect("users:login")
            except User.DoesNotExist:
                messages.error(request, f"Пользователь с почтой {email} не существует")
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset.html", {"form": form})
