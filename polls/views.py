import traceback
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls.base import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.vary import vary_on_cookie
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction
from .models import *
from .utils import *
from .ml import predict_score, get_error, write_change
from . import forms

User = get_user_model()


# Create your views here.
# ==============================================================================
#   访客视图
# ==============================================================================
@cache_control(max_age=1800)
@vary_on_cookie
def index(request):
    """
    首页视图
    """
    logger.debug(settings.MEDIA_URL)
    globalvar = GlobalVar.get()
    return render(request, 'polls/index.html', locals())


# ==============================================================================
#   用户视图
# ==============================================================================

# ------------------------------------------------------------------------------
#   用户验证相关视图
# ------------------------------------------------------------------------------
@never_cache
def register(request):
    """
    注册视图
    """
    template_path = 'polls/register.html'
    if request.user.is_authenticated and not settings.DEBUG:
        # 登录状态不允许注册
        return redirect(reverse('index'))
    register_form = forms.RegisterForm()
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "未知错误"
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
                phone=register_form.cleaned_data['phone'],
                first_name=register_form.cleaned_data['first_name'],
                last_name=register_form.cleaned_data['last_name'],
                person_id=person_id,
                is_active=False  # 默认未激活
            )
            user.set_password(password1)
            try:
                send_activate_email(request, user)
                user.save()
                message = '注册成功，请登录注册邮箱激活账号'
            except Exception as e:
                traceback.print_exc()
                message = '激活邮件发送失败，请联系管理员'
                user.delete()
        else:
            message = register_form.errors.as_text()
    return render(request, template_path, locals())


@never_cache
def activate_account_view(request, uidb64, token):
    """
    激活账号视图
    """
    template_path = 'polls/account_activate_result.html'
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.groups.add(Group.objects.get(name='student'))
        user.save()
        return render(request, template_path, {'message': True})
    else:
        return render(request, template_path, {'message': False})


# ------------------------------------------------------------------------------
#   修改个人信息相关视图
# ------------------------------------------------------------------------------
@never_cache
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


@never_cache
def edit_resume_view(request):
    """
    编辑简历视图
    1. 学生是否能编辑：提交或ddl过了无法编辑，但如果有教师打回则可以编辑
    2. 第一次编辑创建简历对象实例，保存成功则创建ResumeResult对象实例负责保存评分
    """
    template_path = 'polls/editresume.html'
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    user = User.objects.get(id=request.user.id)
    resume = Resume.objects.get_or_create(student=user, defaults={'student': user})[0]
    resume_form = forms.ResumeForm(instance=resume)
    logger.debug(resume.__dict__)
    disable, message = check_disable_or_not(resume)
    if disable:
        return render(request, template_path, locals())
    if request.method == "POST":
        resume_form = forms.ResumeForm(request.POST, instance=resume)
        message = "未知错误"
        if resume_form.is_valid():  # 获取数据
            logger.debug(resume_form.cleaned_data)
            try:
                resume = resume_form.save(commit=False)
                if resume.special_permit:
                    resume.submitted = False
                resume.save()
                logger.debug(resume.__dict__)
                resume_result = ResumeResult.objects.get_or_create(resume=resume)[0]
                resume_result.save()
                message = '修改成功'
            except Exception as e:
                message = '修改失败' + e.__str__()
        else:
            message = resume_form.errors.as_text()
    return render(request, template_path, locals())


@never_cache
@login_required
def check_submit_view(request):
    """
    学生简历自动检查和确认提交视图
    """
    resume = get_object_or_404(Resume, student=request.user.id)
    disable, message = check_disable_or_not(resume)
    errors = check_resume(resume)
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
                            resume.special_permit = False
                            resume.save()
                        disable = True
                        message = '提交成功'
                    except:
                        message = '提交失败'
                else:
                    message = '请确认已阅读通知'
        else:
            confirm_form = forms.ConfirmSubmitForm()
            message = '检验通过'
    else:
        disable = False
        message = '简历部分字段有误'
        check_pass = False
    return render(request, 'polls/checksubmit.html', locals())


# ==============================================================================
#   管理视图
# ==============================================================================

# ------------------------------------------------------------------------------
#   公告相关视图
#   增删改查
# ------------------------------------------------------------------------------
class announce_list_view(ListView):
    """
    所有公告视图，教师（有编辑公告权限）可以看见所有公告，
    学生只能看到已发布的公告
    """
    template_name = 'polls/announce_index.html'
    context_object_name = 'announce_list'
    paginate_by = 10

    def get_queryset(self, request):
        if request.user.is_staff:
            return Announcement.objects.order_by('-public_time')
        else:
            return Announcement.objects.filter(public_time__lte=timezone.now()).order_by('-public_time')

    def get(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return redirect(reverse('login'))
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        return self.render_to_response(context)


@cache_control(max_age=600)
def latest_announce_list_view(request, num=-1):
    """
    返回最新的五条公告，rest接口，在base.html中用AJAX展示
    """
    set = Announcement.objects.filter(
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


@cache_control(max_age=600)
def detail_announce_view(request, pk):
    """
    展示公告详情，需要判断一下是否公开
    """
    announce = Announcement.objects.get(id=pk)
    if announce.public_time > timezone.now() and not (request.user.is_authenticated and request.user.is_staff):
        raise PermissionDenied
    return render(request, 'polls/announce_detail.html', {'announce': announce})


@never_cache
@staff_member_required(login_url=reverse_lazy('login'))
def edit_announce_view(request, pk=0):
    """
    编辑公告详情
    """
    template_path = 'polls/announce_edit.html'
    if pk:
        announce = Announcement.objects.get(id=pk)
    else:
        announce = Announcement.objects.create()
    announce_form = forms.AnnouncementForm(instance=announce)
    if request.method == 'POST':
        announce_form = forms.AnnouncementForm(request.POST, instance=announce)
        message = "未知错误"
        if announce_form.is_valid():
            logger.debug(announce_form.cleaned_data)
            try:
                with transaction.atomic():
                    announce_form.save()
                message = '修改成功'
            except:
                message = '修改失败'
        else:
            message = announce_form.errors.as_text()
    return render(request, template_path, locals())


@never_cache
@staff_member_required(login_url=reverse_lazy('login'))
def delete_announce_view(request, pk):
    """
    确认删除公告视图
    """
    announce = get_object_or_404(Announcement, id=pk)
    if request.method == 'POST':
        announce.delete()
        return redirect(reverse('announce_index'))
    return render(request, 'polls/announce_delete.html', {'announce': announce})


# ------------------------------------------------------------------------------
#   学生管理相关视图
# ------------------------------------------------------------------------------
class StudentListView(ListView):
    """
    学生列表视图
    TODO: 就这里还没写完，需要一个合适的前端模板
    """
    template_name = 'polls/userlist.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        if settings.DEBUG:
            return User.objects.all()
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


@never_cache
@staff_member_required(login_url=reverse_lazy('login'))
def teacher_send_email_view(request):
    """
    教师群发邮件视图
    """
    selected = {'to': [str(i.resume.student.id) for i in ResumeResult.objects.filter(
        admiss=True)]} if request.GET.get('admiss') else {}
    email_form = forms.SendMultiMailForm(initial=selected)
    if request.method == 'POST':
        message = '未知错误'
        email_form = forms.SendMultiMailForm(request.POST, request.FILES)
        files = request.FILES.getlist('attach')
        logger.info(files)
        if email_form.is_valid():
            try:
                to_user = MyUser.objects.filter(id__in=[int(i) for i in email_form.cleaned_data['to']])
                from django.core.mail import EmailMessage
                email = EmailMessage(
                    subject=email_form.cleaned_data['title'],
                    body=render_to_string(
                        'polls/general_email.html', {'content': email_form.cleaned_data['content']}),
                    from_email=settings.EMAIL_HOST_USER,
                    to=[i['email'] for i in to_user.values('email')],
                )
                for f in files:
                    if f.size > 1024 * 1024 * 49:
                        raise Exception('超过50M的文件无法通过附件发送')
                    email.attach(f._name, f.read())
                email.send()
                message = '发送成功'
            except Exception as e:
                message = e.__str__()
                traceback.print_exc()
    return render(request, 'polls/teacher_send_email.html', locals())


# ------------------------------------------------------------------------------
#   系统设置视图
#   设定一些统一的设置，比如截止提交时间，只有管理员有权限
# ------------------------------------------------------------------------------

@staff_member_required(login_url=reverse_lazy('login'))
@never_cache
def set_globalvar_view(request):
    """
    超级管理员设置全局配置视图
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    globalvar = GlobalVar.get()
    globalvar_form = forms.GlobalVarForm(initial=globalvar)
    if request.method == 'POST':
        globalvar_form = forms.GlobalVarForm(request.POST)
        message = '修改失败'
        if globalvar_form.is_valid():
            try:
                GlobalVar.set(globalvar_form.cleaned_data)
                message = '修改成功'
            except Exception as e:
                message = e.__str__()
    return render(request, 'polls/GlobalVar.html', locals())


# ------------------------------------------------------------------------------
#   系统设置视图
#   设定一些统一的设置，比如截止提交时间，只有管理员有权限
# ------------------------------------------------------------------------------
@staff_member_required(login_url=reverse_lazy('login'))
def run_model_view(request):
    """
    选择并运行机器学习评分模型，并显示运行时出现的错误反馈
    """
    model_form = forms.SelectModelForm()
    is_error = False
    if request.method == 'POST':
        model_form = forms.SelectModelForm(request.POST)
        message = '评分失败'
        is_error = True
        if model_form.is_valid():
            try:
                model = MLModel.objects.get(id=int(model_form.cleaned_data['model']))
                feedback = predict_score(model.file)
                write_change(feedback)
                feedback = get_error(feedback)
                if len(feedback) > 0:
                    message = f'{len(feedback)}份简历评分失败'
                else:
                    is_error = False
                    message = '评分成功'
            except Exception as e:
                message = e.__str__()
                traceback.print_exc()
    return render(request, 'polls/run_model.html', locals())
