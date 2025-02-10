python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test Message',
    'pbgnpl@gmail.com',  # From email
    ['coc42060@gmail.com'],  # To email
    fail_silently=False,
)