from django.core.mail import send_mail

send_mail(
    'Test Email',
    'Hello! This is a test email from Django.',
    'jiveshwork16@gmail.com',
    ['jivesh13singasane@gmail.com'],
    fail_silently=False,
)
