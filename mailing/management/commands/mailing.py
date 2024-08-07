import smtplib
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from mailing.models import Mailing, MailingAttempt
import pytz
from django.conf import settings


class Command(BaseCommand):
    help = 'Check mailings and send emails if needed'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        moscow_tz = pytz.timezone(settings.TIME_ZONE)
        msk_time = now.astimezone(moscow_tz)

        mailings = Mailing.objects.filter(status__in=['created', 'started'])

        for mailing in mailings:
            clients = mailing.clients.all()
            for client in clients:
                print(client.email)
            if mailing.status == 'completed':
                continue

            if mailing.status == 'created':
                if self.should_send_mailing(mailing, msk_time):
                    self.send_mailing(mailing)
            elif mailing.status == 'started':
                if mailing.actual_end_time and mailing.actual_end_time <= msk_time:
                    mailing.complete_mailing()
                elif self.should_send_mailing(mailing, msk_time):
                    self.send_mailing(mailing)

    def should_send_mailing(self, mailing, now):
        last_attempt = mailing.attempts.order_by('-timestamp').first()
        if not last_attempt:
            return True


        last_attempt_timestamp_msk = last_attempt.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE))
        print(last_attempt_timestamp_msk)
        delta = now - last_attempt_timestamp_msk
        self.stdout.write(self.style.SUCCESS(f'Mailing {mailing.id} last attempted {delta.days} days ago.'))

        if mailing.periodicity == 'daily' and delta.days >= 1:
            return True
        elif mailing.periodicity == 'weekly' and delta.days >= 7:
            return True
        elif mailing.periodicity == 'monthly' and delta.days >= 30:
            return True

        return False

    def send_mailing(self, mailing):
        recipients = mailing.clients.all()
        subject = mailing.message.subject
        body = mailing.message.body

        for client in recipients:
            try:
                # Отправляем письмо
                server_response = send_mail(
                    subject=subject,
                    message=body,
                    from_email='shutdownrunner@bk.ru',
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = 'success'
            except smtplib.SMTPException as e:
                # При ошибке почтовика получаем ответ сервера - ошибка, которая записывается в e
                server_response = str(e)
                status = 'failed'

            # Записываем попытку рассылки
            MailingAttempt.objects.create(
                mailing=mailing,
                status=status,
                server_response=server_response,
            )

        mailing.start_mailing()
        self.stdout.write(self.style.SUCCESS(f'Mailing {mailing.id} started'))
