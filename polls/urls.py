from django.contrib.auth import logout
from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userlist', views.StudentListView.as_view(), name='userlist'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(template_name='polls/logout.html'), name='logout'),
    
]