import logging
from django.urls.base import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import ListView
# from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction
from .models import *
from .utils import account_activation_token, check_deadline_pass, check_resume, send_activate_email
from . import forms


logger = logging.getLogger(__name__)

# Create your views here.
#==============================================================================
#   访客视图
#==============================================================================

def index(request):
    from django.conf import settings
    logger.debug(settings.MEDIA_URL)
    return render(request, 'polls/index.html', locals())

User = get_user_model()


#==============================================================================
#   管理视图
#==============================================================================

#------------------------------------------------------------------------------
#   用户验证相关视图
#------------------------------------------------------------------------------

def register(request):
    template_path = 'polls/register.html'
    if request.user.is_authenticated and not settings.DEBUG:
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
            if User.objects.filter(username=username).exists():  # 用户名唯一
                message = '用户已经存在，请重新选择用户名！'
                return render(request, template_path, locals())
            if User.objects.filter(email=email).exists():  # 邮箱地址唯一
                message = '该邮箱地址已被注册，请使用别的邮箱！'
                return render(request, template_path, locals())
            if User.objects.filter(person_id=person_id).exists():  # 邮箱地址唯一
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
                person_id=person_id,
                is_active=False # 默认未激活
            )
            user.set_password(password1)
            try:
                send_activate_email(request, user)
                user.save()
                message = '注册成功，请登录注册邮箱激活账号'
            except Exception as e:
                import traceback
                traceback.print_exc()
                message = '激活邮件发送失败，请联系管理员'
                user.delete()
    return render(request, template_path, locals())


def activate_account_view(request, uidb64, token):
    template_path = 'polls/account_activate_result.html'
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, template_path, {'message': True})
    else:
        return render(request, template_path, {'message': False})


#------------------------------------------------------------------------------
#   修改个人信息相关视图
#------------------------------------------------------------------------------

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
                if User.objects.filter(username=username).exclude(id=user.id).exists():  # 用户名唯一
                    message += '用户已经存在，请重新选择用户名！'
                    return render(request, template_path, locals())
                else:
                    user.username = username
            if email != '':
                if User.objects.filter(email=email).exclude(id=user.id).exists():  # 邮箱地址唯一
                    message += '该邮箱地址已被注册！'
                    return render(request, template_path, locals())
                else:
                    user.email = email
            if profile_form.cleaned_data['number'] != '':
                user.number = profile_form.cleaned_data['number']
            if profile_form.cleaned_data['phone'] != '':
                user.phone = profile_form.cleaned_data['phone']
            try:
                with transaction.atomic():
                    user.save()
                message = '修改成功'
            except DatabaseError:
                message = '修改失败'
    return render(request, template_path, locals())


def edit_resume_view(request):
    template_path = 'polls/editresume.html'
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    user = User.objects.get(id=request.user.id)
    resume = Resume.objects.get_or_create(student=user, defaults={'student':user})[0]
    logger.debug(resume.__dict__)
    resume_form = forms.ResumeForm(instance=resume)
    if resume.submitted:
        logger.debug('Resume submitted: {}'.format(resume.submitted))
        message = '简历已提交，无法修改'
        return render(request, template_path, locals())
    elif check_deadline_pass():
        message = '截止提交时间已过'
        return render(request, template_path, locals())
    if request.method == "POST":
        resume_form = forms.ResumeForm(request.POST, instance=resume)
        message = "未知错误"
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


@login_required
def check_submit_view(request):
    user = User.objects.get(id=request.user.id)
    resume = Resume.objects.get(student=user)
    is_submitted = resume.submitted
    errors = check_resume(resume) if not is_submitted else []
    if not len(errors):
        check_pass = True
        if request.method == 'POST':
            confirm_form = forms.ConfirmSubmitForm(request.POST)
            message = '未知错误'
            if confirm_form.is_valid():
                if confirm_form.cleaned_data['i_confirm']:
                    try:
                        with transaction.atomic():
                            resume.submitted = True
                            resume.save()
                        is_submitted = True
                        message = '提交成功'
                    except:
                        message = '提交失败'
                else:
                    message = '请确认已阅读通知'
        else:
            confirm_form = forms.ConfirmSubmitForm()
            message = '检验通过'
    else:
        message = '简历部分字段有误'
        check_pass = False
    return render(request, 'polls/checksubmit.html', locals())


#==============================================================================
#   管理视图
#==============================================================================

#------------------------------------------------------------------------------
#   公告相关视图
#   增删改查
#------------------------------------------------------------------------------
class anounce_list_view(ListView):
    template_name = 'polls/anounce_index.html'
    context_object_name = 'anounce_list'
    paginate_by = 10

    def get_queryset(self, request):
        if request.user.is_staff:
            return Anoucement.objects.order_by('-public_time')
        else:
            return Anoucement.objects.filter(public_time__lte=timezone.now()).order_by('-public_time')

    def get(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return redirect(reverse('login'))
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        return self.render_to_response(context)


def latest_anounce_list_view(request, num=-1):
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

def detail_anounce_view(request, pk):
    anounce = Anoucement.objects.get(id=pk)
    if anounce.public_time > timezone.now() and not (request.user.is_authenticated and request.user.is_staff):
        raise PermissionDenied
    return render(request, 'polls/anounce_detail.html', {'anounce': anounce})


@staff_member_required(login_url=reverse_lazy('login'))
def edit_anounce_view(request, pk=0):
    template_path = 'polls/anounce_edit.html'
    if pk:
        anounce = Anoucement.objects.get(id=pk)
    else:
        anounce = Anoucement.objects.create()
    anounce_form = forms.AnouncementForm(instance=anounce)
    if request.method == 'POST':
        anounce_form = forms.AnouncementForm(request.POST, instance=anounce)
        message = "未知错误"
        if anounce_form.is_valid():
            logger.debug(anounce_form.cleaned_data)
            try:
                with transaction.atomic():
                    anounce_form.save()
                message = '修改成功'
            except:
                message = '修改失败'
        else:
            message = anounce_form.errors.as_text()
    return render(request, template_path, locals())


@staff_member_required(login_url=reverse_lazy('login'))
def delete_anounce_view(request, pk):
    anounce = get_object_or_404(Anoucement, id=pk)
    if request.method == 'POST':
        anounce.delete()
        return redirect(reverse('anounce_index'))
    return render(request, 'polls/anounce_delete.html', {'anounce': anounce})


#------------------------------------------------------------------------------
#   学生管理相关视图
#------------------------------------------------------------------------------
class StudentListView(ListView):
    template_name = 'polls/userlist.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        return User.objects.filter(is_staff=False)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        if not request.user.is_staff:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data
