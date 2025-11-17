from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    code1 = forms.CharField(max_length=1, required=True)
    code2 = forms.CharField(max_length=1, required=True)
    code3 = forms.CharField(max_length=1, required=True)
    code4 = forms.CharField(max_length=1, required=True)
    repeat1 = forms.CharField(max_length=1, required=True)
    repeat2 = forms.CharField(max_length=1, required=True)
    repeat3 = forms.CharField(max_length=1, required=True)
    repeat4 = forms.CharField(max_length=1, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Бұл email бұрыннан тіркелген.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        from .models import Profile
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Бұл телефон нөмірі бұрыннан тіркелген.")
        return phone




class TransferForm(forms.Form):
    receiver_number = forms.CharField(label="Қабылдаушының телефон нөмірі")  # receiver_number
    amount = forms.IntegerField(label="Сома")

class ConfirmCodeForm(forms.Form):
    otp_code = forms.CharField(label="Растаушы код")