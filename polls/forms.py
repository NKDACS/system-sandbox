from django_summernote.fields import SummernoteTextFormField
from polls.models import MLModel, Resume, Announcement
from polls import utils
from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.forms import PasswordResetForm
from django.core.validators import MinLengthValidator
from django_summernote.widgets import SummernoteWidget
from django.contrib.auth import get_user_model
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

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
    phone = forms.CharField(
        label='电话', min_length=11, max_length=11, required=False,
        validators=[MinLengthValidator(11, '请输入11位电话号')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(label='验证码', error_messages={'invalid': '验证码错误'})


class MyPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(label='验证码', error_messages={'invalid': '验证码错误'})


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
        label="工号", required=False,
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
            'aspiration', 'major_choices', 'tutor',
            'university', 'school', 'major', 'gpa',
            'rank', 'major_student_amount', 'cet6',
            'cet6_grades', 'other_prize_penalty', 'others',
        ]
        widgets = {
            'aspiration': forms.Select(attrs={'class': 'form-control'}),
            'major_choices': forms.Select(attrs={'class': 'form-control'}),
            'tutor': forms.Select(attrs={'class': 'form-control'}),
            'university': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control'}),
            'major_student_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'cet6': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left:1rem;'}),
            'cet6_grades': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_prize_penalty': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'maxlength':'1000'}),
            'others': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'maxlength': '1000'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'public_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': SummernoteWidget(),
            'public_time': forms.DateTimeInput()
        }


class ConfirmSubmitForm(forms.Form):
    i_confirm = forms.BooleanField(
        label='我已知晓以上内容，确认提交',
        widget=forms.CheckboxInput(),
        required=True, initial=False
    )


class GlobalVarForm(forms.Form):
    deadline = forms.DateTimeField(
        label='简历提交截止日期', required=True,
        widget=forms.DateTimeInput()
    )
    contact = forms.EmailField(
        label='问题反馈邮箱', required=True,
        widget=forms.TextInput()
    )


class SendMultiMailForm(forms.Form):
    title = forms.CharField(
        label='邮件标题', max_length=32, 
        required=True, initial='通知 - 南开大学统计与数据科学学院推免报名系统',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = SummernoteTextFormField(
        label='邮件正文', required=True,
        widget=SummernoteWidget(attrs={'class': 'form-control'})
    )
    attach = forms.FileField(
        label='附件', allow_empty_file=False,
        max_length=128, required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        q = choices = User.objects.annotate(
            label=Concat('last_name', 'first_name', V('('), 'person_id', V(')'),
            output_field=CharField())
        ).values('id', 'label')
        self.fields['to'] = forms.MultipleChoiceField(
            label='收件人',
            choices=[(o['id'], o['label']) for o in q],
            required=True,
            widget=forms.SelectMultiple(attrs={'class': 'form-control'})
        )


class SelectModelForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'] = forms.ChoiceField(
            label='选择模型',
            choices=MLModel.objects.annotate(
                human_readable=Concat('name', 'version', output_field=CharField())
            ).values_list('id', 'human_readable'),
            widget=forms.Select(),
            required=True
        )

