from polls import utils
from system.settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.urls import reverse

class MyUser(AbstractUser):
    number = models.IntegerField(verbose_name='工号/学号', name='number', blank=True, null=True)
    phone = models.CharField(verbose_name='电话', name='phone', blank=True, max_length=11, 
        validators=[MinLengthValidator(11, '请输入11位有效电话')])
    person_id = models.CharField(
        verbose_name='身份证号', max_length=18,
        unique=True, blank=True, null=True,
        validators=[utils.IDValidator, ]
    )
    first_name = models.CharField(verbose_name='名字', max_length=32)
    last_name = models.CharField(verbose_name='姓氏', max_length=32)
    def get_absolute_url(self):
        return reverse('login')


# class BasicInfo(models.Model):
#     student = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生账号')
#     # fullname = models.CharField(verbose_name='姓名', max_length=32, blank=False)
#     class Meta:
#         verbose_name = '基本信息'


class Resume(models.Model):
    student = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生账号')
    university = models.CharField(verbose_name='学校', choices=utils.UNIVERSITY, max_length=16, blank=True)
    school = models.CharField(verbose_name='学院', max_length=16, blank=True)
    major = models.CharField(verbose_name='本科主修专业', max_length=16, blank=True)
    gpa = models.FloatField(verbose_name='平均学分绩', blank=True)
    rank = models.SmallIntegerField(verbose_name='本科专业内学分绩排名', blank=True)
    major_student_amount = models.IntegerField(verbose_name='本科专业总人数', blank=True)
    cet6 = models.BooleanField(verbose_name='是否通过CET6', default=False)
    other_prize_penalty = models.TextField(verbose_name='其他奖励惩罚', max_length=1024, blank=True)
    others = models.TextField(verbose_name='备注', max_length=1024, blank=True)

    class Meta:
        verbose_name = '简历'
