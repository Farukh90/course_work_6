# Generated by Django 4.2.14 on 2024-08-04 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0004_mailingattempt_client_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailingattempt',
            name='client_email',
        ),
    ]
