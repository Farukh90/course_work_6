import random

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from blog.models import BlogPost
from config import settings
from .forms import (
    ClientForm,
    MessageForm,
    MailingForm,
    MailingAttemptForm,
    MailingModeratorForm,
)
from .models import Client, Message, Mailing, MailingAttempt
from .services import get_cached_articles
from .utils import create_contact_dict, read_JSON_data, write_JSON_data


class HomePageView(View):

    def get(self, request, *args, **kwargs):
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status="started").count()
        unique_clients_count = Client.objects.distinct().count()

        random_articles = get_cached_articles()

        context = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_clients_count": unique_clients_count,
            "random_articles": random_articles,
        }

        return render(request, "mailing/index.html", context)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if self.request.user.is_superuser:
            # Если пользователь администратор, показать всех клиентов
            return Client.objects.all()
        else:
            # Иначе показать клиентов, связанных с текущим пользователем
            return Client.objects.filter(owner=self.request.user)


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_object(self, queryset=None):
        # Получаем объект рассылки
        obj = super().get_object(queryset)

        # Проверяем, является ли текущий пользователь владельцем
        if obj.owner != self.request.user:
            # Если нет, возвращаем 403 Forbidden
            raise PermissionDenied("Вы не можете удалить эту рассылку.")

        return obj


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MessageForm(instance=self.object)
        return context


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.save(owner=self.request.user)
        return redirect(self.success_url)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        # Получаем объект рассылки
        obj = super().get_object(queryset)

        # Проверяем, является ли текущий пользователь владельцем
        if obj.owner != self.request.user:
            # Если нет, возвращаем 403 Forbidden
            raise PermissionDenied("Вы не можете удалить эту рассылку.")
        return obj


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    permission_required = 'mailing.view_mailing'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_mailing"):
            # Менеджеры и администраторы видят все рассылки
            return Mailing.objects.all()
        else:
            # Обычные пользователи видят только свои рассылки
            return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseNotFound(
                "<h1>404 Not Found</h1><p>Страница не найдена. Пожалуйста, авторизуйтесь для доступа.</p>"
            )
        return super().dispatch(request, *args, **kwargs)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        form.save_m2m()  # Сохранение клиентов
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.save()
        form.save_m2m()  # Обновление Many-to-Many связей (клиентов)
        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        mailing = self.get_object()
        if user == mailing.owner:
            return MailingForm
        if user.has_perm("mailing.can_edit_mailing"):
            return MailingModeratorForm
        raise PermissionDenied

    def test_func(self):
        user = self.request.user
        mailing = self.get_object()
        return user == mailing.owner or user.has_perm("mailing.can_edit_mailing")

    def handle_no_permission(self):
        return HttpResponseForbidden(
            "<h1>403 Forbidden</h1><p>У вас нет доступа к этой странице.</p>"
        )


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_object(self, queryset=None):
        # Получаем объект рассылки
        obj = super().get_object(queryset)

        # Проверяем, является ли текущий пользователь владельцем
        if obj.owner != self.request.user:
            # Если нет, возвращаем 403 Forbidden
            raise PermissionDenied("Вы не можете удалить эту рассылку.")

        return obj


class MailingAttemptListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        mailing_id = self.kwargs["mailing_id"]
        return MailingAttempt.objects.filter(mailing_id=mailing_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing_id = self.kwargs["mailing_id"]
        context["mailing"] = get_object_or_404(Mailing, pk=mailing_id)
        context["mailing_id"] = mailing_id
        return context

    def test_func(self):
        mailing_id = self.kwargs["mailing_id"]
        mailing = get_object_or_404(Mailing, pk=mailing_id)
        return self.request.user == mailing.owner

    def handle_no_permission(self):
        return HttpResponseForbidden(
            "<h1>403 Forbidden</h1><p>У вас нет доступа к этой странице.</p>"
        )


class MailingAttemptDetailView(DetailView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_detail.html"


class MailingAttemptCreateView(CreateView):
    model = MailingAttempt
    form_class = MailingAttemptForm
    template_name = "mailing/mailing_attempt_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["mailing"] = self.kwargs["mailing_id"]
        return initial

    def form_valid(self, form):
        form.instance.mailing_id = self.kwargs["mailing_id"]
        return super().form_valid(form)

    def get_success_url(self):
        mailing_id = self.kwargs["mailing_id"]
        return reverse_lazy(
            "mailing:mailing_attempt_list", kwargs={"mailing_id": mailing_id}
        )


class MailingAttemptUpdateView(UpdateView):
    model = MailingAttempt
    form_class = MailingAttemptForm
    template_name = "mailing/mailing_attempt_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailing_id"] = self.object.mailing.id
        return context

    def get_success_url(self):
        return reverse(
            "mailing:mailing_attempt_list",
            kwargs={"mailing_id": self.object.mailing.id},
        )


class MailingAttemptDeleteView(DeleteView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


contacts_base_file = r"contacts.json"


class ContactView(View):
    template_name = "mailing/contacts.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("phone")
        message = request.POST.get("message")
        print(f"{name} ({email}): {message}")

        new_contact = create_contact_dict(name, email, message)

        contacts_base = read_JSON_data(contacts_base_file)

        contacts_base.append(new_contact)

        write_JSON_data(contacts_base_file, contacts_base)

        return render(request, self.template_name)


class RunMailingCommandView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mailing_id = kwargs.get("mailing_id")
        mailing = get_object_or_404(Mailing, id=mailing_id)

        try:
            call_command("check_and_send_mailings")
            messages.success(request, "Команда выполнена успешно.")
        except Exception as e:
            messages.error(request, f"Произошла ошибка при выполнении команды: {e}")

        # return redirect('mailing:mailing_list')
        return redirect(
            reverse("mailing:mailing_attempt_list", kwargs={"mailing_id": mailing_id})
        )


class RunMailingHardCommandView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mailing_id = kwargs.get("mailing_id")
        mailing = get_object_or_404(Mailing, id=mailing_id)

        try:
            call_command("check_and_send_mailings_hard")
            messages.success(request, "Команда выполнена успешно.")
        except Exception as e:
            messages.error(request, f"Произошла ошибка при выполнении команды: {e}")

        # return redirect('mailing:mailing_list')
        return redirect(
            reverse("mailing:mailing_attempt_list", kwargs={"mailing_id": mailing_id})
        )
