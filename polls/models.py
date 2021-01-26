from typing import Tuple
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

class MyUser(AbstractUser):
    number = models.IntegerField(verbose_name='工号/学号', blank=True, null=True)
    phone = models.CharField(verbose_name='电话', unique=True, blank=True, max_length=11, 
        validators=[MinLengthValidator(11, '请输入11位有效电话')])


# Create your models here.
