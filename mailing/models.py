from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()
NULLABLE = {"blank": True, "null": True}


class Client(models.Model):
    email = models.EmailField(verbose_name="e-mail адрес", unique=True)
    full_name = models.CharField(verbose_name="Ф.И.О клиента", max_length=255)
    comment = models.TextField(verbose_name="комментарий", blank=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clients", **NULLABLE
    )

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField(verbose_name="Тема", max_length=255)
    body = models.TextField(verbose_name="Сообщение", blank=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages", **NULLABLE
    )

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Активна"),
        ("completed", "Завершена"),
    ]

    PERIODICITY_CHOICES = [
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
        ("monthly", "Ежемесячно"),
    ]
    description = models.CharField(
        verbose_name="описание", max_length=255, blank=True, null=True
    )
    start_time = models.DateTimeField(verbose_name="дата начала рассылки")
    periodicity = models.CharField(
        verbose_name="периодичность", max_length=10, choices=PERIODICITY_CHOICES
    )
    status = models.CharField(
        verbose_name="статус", max_length=10, choices=STATUS_CHOICES, default="created"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="сообщение"
    )
    clients = models.ManyToManyField(Client, verbose_name="клиенты")
    actual_end_time = models.DateTimeField(
        verbose_name="дата завершения рассылки", blank=True, null=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mailings", **NULLABLE
    )

    def __str__(self):
        return f"Mailing {self.id} - {self.status}"

    def start_mailing(self):
        self.actual_start_time = timezone.now()
        self.status = "started"
        self.save()

    def complete_mailing(self):
        self.actual_end_time = timezone.now()
        self.status = "completed"
        self.save()

    class Meta:
        ordering = ["-start_time"]
        verbose_name = "Mailing"
        verbose_name_plural = "Mailings"
        permissions = [
            ("can_view_mailing", "can view mailing"),
            ("can_edit_mailing", "can edit mailing"),
        ]


class MailingAttempt(models.Model):
    STATUS_CHOICES = [("success", "Успешно"), ("failed", "Не успешно")]

    mailing = models.ForeignKey(
        Mailing, related_name="attempts", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attempt {self.id} - {self.status}"
