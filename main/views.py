from django.contrib.auth import authenticate, login, logout
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Profile
from .forms import RegisterForm
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.conf import settings

from .models import User, TransferOTP , User
from .models import Profile
from django.db import transaction
from django.db import models
from .forms import TransferForm, ConfirmCodeForm

from .utils import send_confirm_code
from .models import Transfer

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout

from django.http import JsonResponse

def logout(request):
    auth_logout(request)
    return redirect("login")
def normalize_phone(phone):
    """Нөмірді +7XXXXXXXXXX форматқа келтіру"""
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    if phone.startswith("7"):
        phone = "+7" + phone[1:]
    return phone

def find_user_ajax(request):
    phone = normalize_phone(request.GET.get("phone", ""))

    try:
        profile = Profile.objects.get(phone=phone)
        user = profile.user
        # Толық ат немесе username
        full_name = user.get_full_name() or user.username
        return JsonResponse({"name": full_name})
    except Profile.DoesNotExist:
        return JsonResponse({"name": "Табылмады"})

def transfer_history(request):
    user = request.user

    # 📝 Жіберілген немесе қабылданған аударымдарды аламыз
    transfers = Transfer.objects.filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).order_by('-created_at')

    return render(request, "main/history.html", {"transfers": transfers})


def transfer(request):
    if request.method == "POST":
        sender_user = request.user
        sender_profile = sender_user.profile

        # Түзетілген жол
        receiver_number = request.POST.get("receiver_phone")
        amount = float(request.POST.get("amount"))

        if sender_profile.balance < amount:
            return render(request, "main/transfer.html", {"error": "Баланс жеткіліксіз"})

        # OTP кодын генерациялау
        otp_code = str(random.randint(100000, 999999))
        print("Generated OTP:", otp_code)

        # Базада сақтау
        TransferOTP.objects.create(
            user=sender_user,
            code=otp_code,
            amount=amount,
            receiver_number=receiver_number
        )

        # Email жіберу
        send_mail(
            subject="Аударма кодын растау",
            message=f"Сіз жасағыңыз келген аударым үшін код: {otp_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[sender_user.email],
            fail_silently=False,
        )
        print("Email sent")

        return redirect("confirm_transfer")

    return render(request, "main/transfer.html")


from django.contrib import messages
from django.shortcuts import render, redirect
from .models import TransferOTP, Profile, Transfer

@transaction.atomic
def confirm_transfer(request):
    if request.method == "POST":
        code = request.POST.get("otp_code")
        if not code:
            messages.error(request, "Код енгізілмеген")
            return redirect("confirm_transfer")

        try:
            otp = TransferOTP.objects.get(user=request.user, code=code, verified=False)
        except TransferOTP.DoesNotExist:
            messages.error(request, "Код дұрыс емес")
            return redirect("confirm_transfer")

        # Аударымды жасау
        sender_profile = request.user.profile
        try:
            receiver_profile = Profile.objects.get(phone=otp.receiver_number)
        except Profile.DoesNotExist:
            messages.error(request, "Алушы табылмады")
            return redirect("confirm_transfer")

        sender_profile.balance -= otp.amount
        receiver_profile.balance += otp.amount

        sender_profile.save()
        receiver_profile.save()

        # OTP-ны растау
        otp.verified = True
        otp.save()

        # -----------------------------
        # Transfer тарихына жазу алдында тексеру
        print("Sender ID:", request.user.id)
        print("Receiver ID:", receiver_profile.user.id)
        print("Amount:", otp.amount)

        t = Transfer.objects.create(
            sender=request.user,
            receiver=receiver_profile.user,
            amount=otp.amount
        )
        print("Saved transfer ID:", t.id)
        # -----------------------------

        # Сәттілік хабарламасы
        messages.success(request, f"{otp.amount} ₸ сәтті аударылды {receiver_profile.user.get_full_name()}")

        # Аударымнан кейін Transfer History бетіне бағыттау
        return redirect("transfer")  # redirect өзгертілді

    return render(request, "main/confirm.html")


def history(request):
    user = request.user
    transfers = Transfer.objects.filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).order_by('-created_at')
    return render(request, "main/history.html", {"transfers": transfers})

def mybank(request):
    return render(request, 'main/my_bank.html')

def base(request):
    return render(request, 'main/base.html')

def dashboard(request):
    return render(request, 'main/dashboard.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        code = ''.join([
            request.POST.get('repeat1', ''),
            request.POST.get('repeat2', ''),
            request.POST.get('repeat3', ''),
            request.POST.get('repeat4', '')
        ])

        # Мұнда кодты тексеру логикасы
        # Мысалы: User моделінде code сақталған делік
        try:
            user = User.objects.get(email=email)
            profile = user.profile  # Егер Profile моделінде code болса
            if profile.secret_code == code:
                login(request, user)
                return redirect('mybank')  # Dashboard-қа бағыттау
            else:
                messages.error(request, "Код дұрыс емес")
        except User.DoesNotExist:
            messages.error(request, "Пайдаланушы табылмады")

    return render(request, 'main/login.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 4 таңбалы secret code
            secret_code = ''.join([form.cleaned_data[f'code{i}'] for i in range(1,5)])
            repeat_code = ''.join([form.cleaned_data[f'repeat{i}'] for i in range(1,5)])

            if secret_code != repeat_code:
                messages.error(request, "Кодтар сәйкес емес!")
                return redirect('register')

            # 6 таңбалы email коды
            email_code = str(random.randint(100000, 999999))
            request.session['email_code'] = email_code
            request.session['user_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'secret_code': secret_code
            }

            # Email жіберу
            send_mail(
                'Тіркеу коды',
                f'Сіздің тіркеу кодыңыз: {email_code}',
                'from@example.com',
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            return redirect('verify_email')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


def verify_email(request):
    if request.method == "POST":
        input_code = request.POST.get('email_code')
        session_code = request.session.get('email_code')
        if input_code == session_code:
            data = request.session.get('user_data')
            user = User.objects.create_user(username=data['username'], email=data['email'])
            profile = Profile.objects.create(
                user=user,
                phone=data['phone'],
                secret_code=data['secret_code'],
                balance=50000  # тіркелген кезде баланс
            )
            # session-ды тазалау
            del request.session['email_code']
            del request.session['user_data']
            messages.success(request, "Тіркелу сәтті өтті!")
            return redirect('login')
        else:
            messages.error(request, "Код дұрыс емес!")
            return redirect('verify_email')
    return render(request, 'main/verify_email.html')


def send_code_email(user_email, code):
    send_mail(
        'Аударымды растау коды',
        f'Сіздің аударым код: {code}',
        'webmaster@localhost',
        [user_email],
        fail_silently=False,
    )
