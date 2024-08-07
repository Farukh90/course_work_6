import logging
import smtplib
from django.utils import timezone
import pytz
from mailing.models import Mailing, MailingAttempt
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger("mailing")


def check_and_send_mailings():
    now = timezone.now()
    msk_time = now.astimezone(pytz.timezone(settings.TIME_ZONE))

    mailings = Mailing.objects.filter(status__in=["created", "started"])
    logger.debug(f"Найдено {mailings.count()} рассылок для обработки.")

    for mailing in mailings:
        if mailing.status == "completed":
            logger.debug(f"Рассылка {mailing.id} уже завершена.")
            continue

        if mailing.status == "created":
            if should_send_mailing(mailing, msk_time):
                send_mailing(mailing.id)
        elif mailing.status == "started":
            if mailing.actual_end_time and mailing.actual_end_time <= msk_time:
                mailing.complete_mailing()
            elif should_send_mailing(mailing, msk_time):
                send_mailing(mailing.id)


def check_and_send_mailings_hard():
    mailings = Mailing.objects.filter(status__in=["created", "started"])
    logger.debug(f"Найдено {mailings.count()} рассылок для обработки.")

    for mailing in mailings:
        try:
            if mailing.status != "completed":
                logger.debug(
                    f"Отправка рассылки {mailing.id} со статусом {mailing.status}."
                )
                send_mailing(mailing.id)
            else:
                logger.debug(f"Рассылка {mailing.id} уже завершена.")
        except Exception as e:
            logger.error(
                f"Ошибка при обработке рассылки {mailing.id}: {str(e)}", exc_info=True
            )


def should_send_mailing(mailing, now):
    pass
    last_attempt = mailing.attempts.order_by("-timestamp").first()
    if not last_attempt:
        return True

    last_attempt_timestamp_msk = last_attempt.timestamp.astimezone(
        pytz.timezone(settings.TIME_ZONE)
    )
    delta = now - last_attempt_timestamp_msk
    logger.debug(
        f"Последняя попытка рассылки {mailing.description}: {last_attempt_timestamp_msk}, {delta.days} дней назад."
    )
    if mailing.periodicity == "daily" and delta.days >= 1:
        return True
    elif mailing.periodicity == "weekly" and delta.days >= 7:
        return True
    elif mailing.periodicity == "monthly" and delta.days >= 30:
        return True

    return False


def send_mailing(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)
    try:
        # Отправляем рассылку
        server_response = send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[client.email for client in mailing.clients.all()],
            fail_silently=False,
        )
        # Создаем запись о попытке рассылки если все ок
        MailingAttempt.objects.create(
            mailing=mailing, status="success", server_response=str(server_response)
        )
        mailing.start_mailing()
        logger.info(f"Рассылка {mailing.description} начата.")

    except smtplib.SMTPException as e:
        # Создаем запись о попытке рассылки в случае ошибки
        MailingAttempt.objects.create(
            mailing=mailing, status="failed", server_response=str(e)
        )
        logger.error(f"Ошибка при попытке рассылки произошла ошибка {e}")


import json
import os.path


def create_contact_dict(name: str, phone: str, message: str) -> dict:
    contact_data = {"name": name, "phone": phone, "message": message}

    return contact_data


def read_JSON_data(file_path: str) -> list:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except UnicodeDecodeError as e:
            print(f"ошибка {e}")
            with open(file_path, "r", encoding="windows-1251") as f:
                data = json.load(f)

    else:
        data = []
        print(f"файл {file_path} не существует")
    return data


def write_JSON_data(file_path: str, data) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    check_and_send_mailings()
