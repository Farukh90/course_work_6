from django.db import models
from django.utils import timezone

class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена')
    ]

    PERIODICITY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    description = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField()
    periodicity = models.CharField(max_length=10, choices=PERIODICITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    actual_start_time = models.DateTimeField(blank=True, null=True)
    actual_end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Mailing {self.id} - {self.status}'

    def start_mailing(self):
        self.actual_start_time = timezone.now()
        self.status = 'started'
        self.save()

    def complete_mailing(self):
        self.actual_end_time = timezone.now()
        self.status = 'completed'
        self.save()

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Mailing'
        verbose_name_plural = 'Mailings'


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно')
    ]

    mailing = models.ForeignKey(Mailing, related_name='attempts', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True, null=True)
    client_email = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f'Attempt {self.id} - {self.status}'
