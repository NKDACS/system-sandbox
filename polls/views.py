import logging
from django.urls.base import reverse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import *
from . import forms

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        'content1': '研究生推免报名系统',
        'content2': '南开大学统计与数据科学学院',
        'content3': '测试一下'
    }
    return render(request, 'polls/index.html', context)

User = get_user_model()

class StudentListView(ListView):
    template_name = 'polls/userlist.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        return User.objects.get_queryset().all()
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        if not request.user.is_staff:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


def register(request):
    template_path = 'polls/register.html'
    if request.user.is_authenticated:
        # 登录状态不允许注册
        return redirect(reverse('index'))
    register_form = forms.RegisterForm()
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "验证码错误"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            person_id = register_form.cleaned_data['person_id']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, template_path, locals())
            same_name_user = User.objects.filter(username=username)
            if same_name_user:  # 用户名唯一
                message = '用户已经存在，请重新选择用户名！'
                return render(request, template_path, locals())
            same_email_user = User.objects.filter(email=email)
            if same_email_user:  # 邮箱地址唯一
                message = '该邮箱地址已被注册，请使用别的邮箱！'
                return render(request, template_path, locals())
            same_id_user = User.objects.filter(person_id=person_id)
            if same_id_user:  # 邮箱地址唯一
                message = '该身份证号已被注册，如非本人操作请联系管理员！'
                return render(request, template_path, locals())
            # 当一切都OK的情况下，创建新用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
                number=register_form.cleaned_data['number'],
                phone=register_form.cleaned_data['phone'],
                first_name=register_form.cleaned_data['first_name'],
                last_name=register_form.cleaned_data['last_name'],
                person_id=person_id
            )
            user.set_password(password1)
            user.save()
            return redirect(reverse('login'))  # 自动跳转到登录页面
    return render(request, template_path, locals())


def edit_profile_view(request):
    template_path = 'polls/editprofile.html'
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    profile_form = forms.UserProfileForm()
    if request.method == "POST":
        profile_form = forms.UserProfileForm(request.POST)
        message = "更新失败，输入不符合要求："
        if profile_form.is_valid():  # 获取数据
            username = profile_form.cleaned_data['username']
            password1 = profile_form.cleaned_data['password1']
            password2 = profile_form.cleaned_data['password2']
            email = profile_form.cleaned_data['email']
            logger.info(profile_form.cleaned_data)
            user = User.objects.filter(id=request.user.id).first()
            if ((password1 is None) ^ (password2 is None)) or password1 != password2:
                message += "两次输入的密码不同！"
                return render(request, template_path, locals())
            same_name_user = User.objects.filter(username=username).exclude(id=request.user.id)
            if same_name_user:  # 用户名唯一
                message += '用户已经存在，请重新选择用户名！'
                return render(request, template_path, locals())
            if email != '':
                same_email_user = User.objects.filter(email=email).exclude(id=request.user.id)
                if same_email_user:  # 邮箱地址唯一
                    message += '该邮箱地址已被注册！'
                    return render(request, template_path, locals())
            message = '修改成功'
            
    return render(request, template_path, locals())

def edit_resume_view(request):
    pass
