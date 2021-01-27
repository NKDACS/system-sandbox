from django.contrib.auth import get_user_model
from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.forms import PasswordResetForm
from django.core.validators import MinLengthValidator

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    number = forms.IntegerField(
        label="学号/工号(选填)", required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='电话', min_length=11, max_length=11, required=True,
        validators=[MinLengthValidator(11, '请输入11位电话号')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(label='验证码')


class MyPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(label='验证码')