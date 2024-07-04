import logging
from django.utils import timezone
import pytz
from smtplib import SMTPException
from mailing.models import Mailing, MailingAttempt
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger('mailing')

def check_and_send_mailings():
    now = timezone.now()
    msk_time = now.astimezone(pytz.timezone(settings.TIME_ZONE))


    mailings = Mailing.objects.filter(status__in=['created', 'started'])
    logger.debug(f'Найдено {mailings.count()} рассылок для обработки.')

    for mailing in mailings:
        if mailing.status == 'completed':
            logger.debug(f'Рассылка {mailing.id} уже завершена.')
            continue

        if mailing.status == 'created':
            if should_send_mailing(mailing, msk_time):
                send_mailing(mailing)
        elif mailing.status == 'started':
            if mailing.actual_end_time and mailing.actual_end_time <= msk_time:
                mailing.complete_mailing()
            elif should_send_mailing(mailing, msk_time):
                send_mailing(mailing)

def should_send_mailing(mailing, now):
    last_attempt = mailing.attempts.order_by('-timestamp').first()
    if not last_attempt:
        return True

    last_attempt_timestamp_msk = last_attempt.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE))
    delta = now - last_attempt_timestamp_msk
    logger.debug(f'Последняя попытка рассылки {mailing.description}: {last_attempt_timestamp_msk}, {delta.days} дней назад.')
    if mailing.periodicity == 'daily' and delta.days >= 1:
        return True
    elif mailing.periodicity == 'weekly' and delta.days >= 7:
        return True
    elif mailing.periodicity == 'monthly' and delta.days >= 30:
        return True

    return False

def send_mailing(mailing):
    recipients = mailing.clients.all()
    subject = mailing.message.subject
    body = mailing.message.body

    for client in recipients:
        try:
            # Отправляем письмо
            server_response = send_mail(
                subject=subject,
                message=body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False,
            )
            status = 'success'
            logger.info(f'Письмо успешно отправлено клиенту {client.email} для рассылки {mailing.description}.')
        except SMTPException as e:
            # При ошибке почтовика получаем ответ сервера - ошибка, которая записывается в e
            server_response = str(e)
            status = 'failed'
            logger.error(f'Ошибка при отправке письма клиенту {client.email} для рассылки {mailing.description}: {server_response}')

        # Записываем попытку рассылки
        MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=server_response,
            client_email=client.email
        )

    mailing.start_mailing()
    logger.info(f'Рассылка {mailing.description} начата.')

# Пример использования функций:
if __name__ == "__main__":
    check_and_send_mailings()
