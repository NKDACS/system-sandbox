import logging
from django.urls.base import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView, FormView
from .models import *
from .forms import *

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    context = {'content1': '介似打后端返回的玩意'}
    return render(request, 'polls/index.html', context)


User = get_user_model()
class StudentListView(generic.ListView):
    template_name = 'polls/userlist.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        return User.objects.get_queryset().all()


class RegisterView(CreateView):
    template_name = 'polls/register.html'
    model = MyUser
    fields = ['username', 'password', 'email', 'number', 'phone']

    def form_invalid(self, form):        # 定义表对象没有添加失败后跳转到的页面。
        return HttpResponse("form is invalid. this is just an HttpResponse object")


def register(request):
    if request.user.is_authenticated:
        # 登录状态不允许注册
        return redirect("/")
    register_form = RegisterForm()
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "验证码错误"
        if register_form.is_valid():  # 获取数据
            logger.warning(register_form.cleaned_data['captcha'])
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            phone = register_form.cleaned_data['phone']
            number = register_form.cleaned_data['number']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'polls/register.html', locals())
            same_name_user = User.objects.filter(username=username)
            if same_name_user:  # 用户名唯一
                message = '用户已经存在，请重新选择用户名！'
                return render(request, 'polls/register.html', locals())
            same_email_user = User.objects.filter(email=email)
            if same_email_user:  # 邮箱地址唯一
                message = '该邮箱地址已被注册，请使用别的邮箱！'
                return render(request, 'polls/register.html', locals())
            # 当一切都OK的情况下，创建新用户
            user = User.objects.create_user(
                username = username,
                email = email,
                password = None,
                number = number,
                phone = phone
            )
            user.set_password(password1)
            user.save()
            return redirect(reverse('login'))  # 自动跳转到登录页面
    return render(request, 'polls/register.html', locals())


# class CustomPasswordResetView(PasswordResetView):
#     template_name = 'polls/passwdreset.html'
#     email_template_name = 'polls/password_reset_email.html'
#     form_class = CustomPasswordResetForm