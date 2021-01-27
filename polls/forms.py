from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django import forms

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    #实现'邮箱未注册'的提示
    def clean_email(self):
        email = self.cleaned_date.get('email', '')
        if not User.objects.filter(email=email):
            raise forms.ValidationError('邮箱未注册')
        return email