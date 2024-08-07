from django.core.management.base import BaseCommand
from mailing.utils import check_and_send_mailings_hard


class Command(BaseCommand):
    help = "check and send"

    def handle(self, *args, **kwargs):
        check_and_send_mailings_hard()
        self.stdout.write(self.style.SUCCESS("все ок"))
