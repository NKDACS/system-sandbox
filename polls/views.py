from polls.forms import CustomPasswordResetForm
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from django.contrib.auth.views import PasswordResetView
from .models import MyUser

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

# class CustomPasswordResetView(PasswordResetView):
#     template_name = 'polls/passwdreset.html'
#     email_template_name = 'polls/password_reset_email.html'
#     form_class = CustomPasswordResetForm