from django.urls.base import reverse_lazy
from polls.forms import CustomPasswordResetForm
from django.conf.urls import url
from django.contrib.auth import logout
from django.urls import path
from django.contrib.auth.views import *

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userlist', views.StudentListView.as_view(), name='userlist'),
    path('login', LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='polls/logout.html'), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    #密码重置链接
    url(
        r'^password_reset/$', 
        PasswordResetView.as_view(
            # form_class=CustomPasswordResetForm,
            template_name = 'polls/passwdreset.html',
            email_template_name = 'polls/password_reset_email.html',
            success_url = reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),
    #密码重置邮件发送完成后的页面
    url(
        r'^password_reset/done/$', 
        PasswordResetDoneView.as_view(template_name='polls/password_reset_done.html'), 
        name='password_reset_done'),
    #用户通过邮箱打开的重置密码页面
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        PasswordResetConfirmView.as_view(
            template_name='polls/password_reset_confirm.html',
            success_url = reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm',
    ),
    #密码重置完成后跳转的页面
    url(
        r'^reset/done/$',
        PasswordResetCompleteView.as_view(template_name='polls/password_reset_complete.html'), 
        name='password_reset_complete'),
]