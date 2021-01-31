from polls.models import Resume, Anoucement
from polls import utils
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
    first_name = forms.CharField(label='名字', max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='姓氏', max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    person_id = forms.CharField(
        label='身份证号', max_length=18, 
        validators=[utils.IDValidator],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    number = forms.IntegerField(
        label="学号/工号(选填)", required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='电话', min_length=11, max_length=11, required=False,
        validators=[MinLengthValidator(11, '请输入11位电话号')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(label='验证码')


class MyPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(label='验证码')


class UserProfileForm(forms.Form):
    username = forms.CharField(
        label="用户名", max_length=128, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label="密码", max_length=256, required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label="确认密码", max_length=256, required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(
        label="邮箱地址", required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))
    number = forms.IntegerField(
        label="学号/工号(选填)", required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='电话', min_length=11, max_length=11, required=False,
        validators=[MinLengthValidator(11, '请输入11位电话号')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [ 
            'university', 'school', 'major', 'gpa',
            'rank', 'major_student_amount', 'cet6',
            'other_prize_penalty', 'others',
        ]
        widgets = {
            # 'university': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control'}),
            'major_student_amout': forms.NumberInput(attrs={'class': 'form-control'}),
            'cet6': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left:1rem;'}),
            'other_prize_penalty': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'maxlength':'1000'}),
            'others': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'maxlength': '1000'}),
        }


class AnouncementForm(forms.ModelForm):
    class Meta:
        model = Anoucement
        fields = '__all__'
