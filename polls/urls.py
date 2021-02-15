from django.urls.base import reverse_lazy
from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import *

from . import views
from .forms import MyPasswordResetForm

urlpatterns = [
    path('', views.index, name='index'),
    path('login',
        LoginView.as_view(
            template_name='polls/login.html',
            redirect_authenticated_user=True
        ), 
        name='login'),
    path('logout', LogoutView.as_view(template_name='polls/logout.html'),name='logout'),
    path('userlist', views.StudentListView.as_view(), name='userlist'),
    path('register/', views.register, name='register'),
    path('edit/profile/', views.edit_profile_view, name='editprofile'),
    path('edit/resume/', views.edit_resume_view, name='editresume'),
    path('edit/checksubmit/', views.check_submit_view, name='check_and_submit'),
    path('anounce/index/', views.anounce_list_view.as_view(), name='anounce_index'),
    path('anounce/latest/<int:num>/', views.latest_anounce_list_view, name='anounce_list'),
    path('anounce/<int:pk>/', views.detail_anounce_view, name='anounce_detail'),
    path('anounce/edit/', views.edit_anounce_view, name='anounce_edit'),
    path('anounce/edit/<int:pk>/', views.edit_anounce_view, name='anounce_edit'),
    path('anounce/delete/<int:pk>/', views.delete_anounce_view, name='anounce_delete'),
    #密码重置链接
    url(
        r'^password_reset/$', 
        PasswordResetView.as_view(
            form_class=MyPasswordResetForm,
            template_name = 'polls/passwdreset.html',
            email_template_name = 'polls/password_reset_email.html',
            subject_template_name = 'polls/password_reset_subject.txt',
            success_url = reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),
    #密码重置邮件发送完成后的页面
    url(
        r'^password_reset/done/$', 
        PasswordResetDoneView.as_view(template_name='polls/password_reset_done.html'), 
        name='password_reset_done'
    ),
    #用户通过邮箱打开的重置密码页面
    url(
        r'^reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$', 
        PasswordResetConfirmView.as_view(
            template_name='polls/password_reset_confirm.html',
            success_url = reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm',
    ),
    #用户激活页面
    url(
        r'^activate_acount/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/$',
        views.activate_account_view,
        name='activate_account',
    ),
    #密码重置完成后跳转的页面
    url(
        r'^reset/done/$',
        PasswordResetCompleteView.as_view(template_name='polls/password_reset_complete.html'), 
        name='password_reset_complete'
    ),
    #管理“全局设置”url
    path('globalvar/', views.set_globalvar_view, name='globalvar'),
    #群发邮件
    url(r'^teacher_email/$', views.teacher_send_email_view, name='teacher_send_email'),
    path('model/', views.run_model_view, name='run_model'),
]
