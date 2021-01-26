from system.settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

class MyUser(AbstractUser):
    number = models.IntegerField(verbose_name='工号/学号', blank=True, null=True)
    phone = models.CharField(verbose_name='电话', unique=True, blank=True, max_length=11, 
        validators=[MinLengthValidator(11, '请输入11位有效电话')])

UNIVERSITY = [
    ('天津',
        [('4112010055', '南开大学')]
    ),
    ('北京', 
        [
            ('4111010003', '清华大学'),
            ('4111010001', '北京大学'),
            ('4111010007', '北京理工大学')
        ]
    )
]

class Resume(models.Model):
    student = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生账号')
    university = models.CharField(verbose_name='学校', choices=UNIVERSITY, max_length=16, blank=True)
    school = models.CharField(verbose_name='学院', max_length=16, blank=True)
    major = models.CharField(verbose_name='本科主修专业', max_length=16, blank=True)
    gpa = models.FloatField(verbose_name='百分制学分绩', blank=True)
    rank = models.SmallIntegerField(verbose_name='本科专业内学分绩排名', blank=True)
    major_student_amount = models.IntegerField(verbose_name='本科专业总人数', blank=True)
    
    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'