from django.shortcuts import render
# from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView

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


class UserLoginView(LoginView):
    template_name = 'polls/login.html'

def register_view(request):
    pass
    return render(request, 'polls/register.html')