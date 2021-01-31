"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from .settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('polls.urls')),
    url(r'^captcha', include('captcha.urls')),
    path('summernote/', include('django_summernote.urls')),
    # 用于上传图片文件，也可以上传其他文件word,ppt等。
    path('media/<path:path>', serve, {'document_root': MEDIA_ROOT}),
    # 用于加载静态文件
    path('static/<path:path>', serve, {'document_root': STATIC_ROOT}),  
]
