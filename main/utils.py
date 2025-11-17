import random
from django.core.mail import send_mail

def send_confirm_code(email):
    code = random.randint(100000, 999999)
    send_mail(
        subject="Аударымды растау",
        message=f"Сіздің аударымды растау кодыңыз: {code}",
        from_email="noreply@yourbank.kz",
        recipient_list=[email],
    )
    return code
