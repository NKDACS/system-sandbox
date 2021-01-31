import logging
from django.urls.base import reverse
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.core.serializers import serialize
from .models import *
from . import forms

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        'content1': '研究生推免报名系统',
        'content2': '南开大学统计与数据科学学院',
        'content3': '允公允能，日新月异'
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
    user = User.objects.get(id=request.user.id)
    logger.debug(user.__dict__)
    profile_form = forms.UserProfileForm(initial=user.__dict__)
    if request.method == "POST":
        profile_form = forms.UserProfileForm(request.POST)
        message = "更新失败，输入不符合要求："
        if profile_form.is_valid():  # 获取数据
            username = profile_form.cleaned_data['username']
            password1 = profile_form.cleaned_data['password1']
            password2 = profile_form.cleaned_data['password2']
            email = profile_form.cleaned_data['email']
            logger.debug(profile_form.cleaned_data)
            if password1 != '' or password2 != '':
                if password1 == '' or password2 == '' or password1 != password2:
                    message += "两次输入的密码不同！"
                    return render(request, template_path, locals())
                else:
                    user.set_password(password1)
            if username is not None:
                same_name_user = User.objects.filter(username=username).exclude(id=user.id)
                if same_name_user:  # 用户名唯一
                    message += '用户已经存在，请重新选择用户名！'
                    return render(request, template_path, locals())
                else:
                    user.username = username
            if email != '':
                same_email_user = User.objects.filter(email=email).exclude(id=user.id)
                if same_email_user:  # 邮箱地址唯一
                    message += '该邮箱地址已被注册！'
                    return render(request, template_path, locals())
                else:
                    user.email = email
            if profile_form.cleaned_data['number'] != '':
                user.number = profile_form.cleaned_data['number']
            if profile_form.cleaned_data['phone'] != '':
                user.phone = profile_form.cleaned_data['phone']
            try:
                user.save()
                message = '修改成功'
            except:
                message = '修改失败'
    return render(request, template_path, locals())


def edit_resume_view(request):
    template_path = 'polls/editresume.html'
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    user = User.objects.get(id=request.user.id)
    resume = Resume.objects.get_or_create(student=user, defaults={'student':user})[0]
    logger.info(resume.__dict__)
    resume_form = forms.ResumeForm(instance=resume)
    if request.method == "POST":
        resume_form = forms.ResumeForm(request.POST, instance=resume)
        message = "更新失败，输入不符合要求："
        if resume_form.is_valid():  # 获取数据
            logger.debug(resume_form.cleaned_data)
            try:
                resume_form.save()
                message = '修改成功'
            except:
                message = '修改失败'
        else:
            message = resume_form.errors.as_text()
    return render(request, template_path, locals())


class AnounceListView(ListView):
    template_name = 'polls/anounce_index.html'
    context_object_name = 'anounce_list'
    paginate_by = 10

    def get_queryset(self):
        return Anoucement.objects.filter(public_time__lte=timezone.now()).order_by('-public_time')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        n = self.get_queryset().count() // self.paginate_by + 1
        context['num_list_left'] = list(range(1, min(4, n+1)))
        context['num_list_right'] = list(range(max(min(4, n+1), n-2), n+1))
        return context


def AnounceLatestListView(request, num=-1):
    set = Anoucement.objects.filter(
        public_time__lte=timezone.now()).order_by('-public_time').values('id', 'title', 'public_time')
    if num != -1:
        set = set[:num]
    data = {'list': []}
    for i in set:
        data['list'].append({
            'id': i['id'], 'title': i['title'], 
            'public_time': i['public_time'].strftime("%Y-%m-%d")
        })
    return JsonResponse(data)

def AnounceDetailView(request, pk):
    anounce = Anoucement.objects.get(id=pk)
    if anounce.public_time > timezone.now() and not (request.user.is_authenticated and request.user.is_staff):
        raise PermissionDenied
    return render(request, 'polls/anounce_detail.html', locals())
