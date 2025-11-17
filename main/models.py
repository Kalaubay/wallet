from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone





class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, unique=True)
    secret_code = models.CharField(max_length=4)  # 4 таңбалы сан
    balance = models.IntegerField(default=0)
    username = models.CharField(max_length=150, blank=True)  # Жаңа өріс

    def save(self, *args, **kwargs):
        self.username = self.user.username  # Әрдайым User.username-ді көшіріп қоямыз
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class TransferOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    receiver_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"

class Transfer(models.Model):
    sender = models.ForeignKey(User, related_name="sent_transfers", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_transfers", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.amount}"
