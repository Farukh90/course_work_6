фикстуры в корне проекта.

для конфиденциальных настроек есть файл .env(sample)

Для запуска шедулера необходимо вызвать команду:
python manage.py runapscheduler

для создания админа команда:
python manage.py csu 
admin@mail.com
пароль 123

для отправки рассылки через командную строку команда:
python manage.py check_and_send_mailings

