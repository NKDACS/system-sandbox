from polls import utils
from system.settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.urls import reverse
from django.utils import timezone
from django_summernote.fields import SummernoteTextField

class MyUser(AbstractUser):
    number = models.PositiveIntegerField(verbose_name='工号', name='number', blank=True, null=True)
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


class Anoucement(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    content = SummernoteTextField(verbose_name='内容', null=True)
    # create_timestamp = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_edit_timestamp = models.DateTimeField(verbose_name='最后编辑时间', auto_now=True)
    public_time = models.DateTimeField(verbose_name='公布时间', default=timezone.now)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        indexes = [models.Index(fields=['-public_time'])]

    def __str__(self):
        return self.title


class Resume(models.Model):
    student = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生账号')
    ASPIRATIONS = (
        (0, '专硕'),
        (1, '学硕'),
        (2, '直博')
    )
    aspiration = models.CharField(verbose_name='志愿', choices=ASPIRATIONS, max_length=16, blank=True)
    MAJORS = (
        (0, '统计学'),
        (1, '应用统计')
    )
    TEACHERS = (
        (0, '王兆军'),
        (1, '刘民千'),
        (2, '邹长亮')
    )
    major_choices = models.CharField(verbose_name='研究生报名专业', choices=MAJORS, max_length=16, blank=True)
    tutor = models.CharField(verbose_name='直博生意向导师', choices=TEACHERS,max_length=16, blank=True)
    university = models.CharField(verbose_name='学校', choices=utils.UNIVERSITY, max_length=16, blank=True)
    school = models.CharField(verbose_name='学院', max_length=16, blank=True)
    major = models.CharField(verbose_name='本科主修专业', max_length=16, blank=True)
    gpa = models.FloatField(verbose_name='平均学分绩', null=True, blank=True)
    rank = models.PositiveSmallIntegerField(verbose_name='本科专业内学分绩排名', null=True, blank=True)
    major_student_amount = models.PositiveIntegerField(verbose_name='本科专业总人数', null=True, blank=True)
    cet6 = models.BooleanField(verbose_name='是否通过cet6', default=False, blank=False)
    cet6_grades = models.FloatField(verbose_name='CET6成绩', null=True, blank=True)
    other_prize_penalty = models.TextField(verbose_name='其他奖励惩罚', max_length=1024, blank=True)
    others = models.TextField(verbose_name='备注', max_length=1024, blank=True)
    submitted = models.BooleanField(verbose_name='是否已提交', default=False, blank=False)
    special_permit = models.BooleanField(verbose_name='是否打回修改', default=False, blank=False)

    TYPE_CHOICES = (
        (u'Master', u'硕士'),
        (u'DDS', u'直博生'),
    )
    MAJOR_CHOICES = (
        (u'统计学', u'统计学'),
        (u'应用统计', u'应用统计'),
    )
    enrollment_type = models.CharField(verbose_name='招生类型', default='', choices=TYPE_CHOICES, max_length=6)
    enrollment_major = models.CharField(verbose_name='报考专业', default='', choices=MAJOR_CHOICES, max_length=10)
    enrollment_tutor = models.CharField(verbose_name='意向导师', max_length=20, blank=True)

    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'


class ResumeResult(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, verbose_name='对应简历')
    score = models.FloatField(verbose_name='建议得分', default=0)
    rank = models.IntegerField(verbose_name='建议排名', default=0, blank=True)
    admiss = models.BooleanField(verbose_name='录取', default=False, blank=False)

    class Meta:
        verbose_name = '简历评定'
        verbose_name_plural = '简历评定'


class MLModel(models.Model):
    file = models.FileField(upload_to='models/', verbose_name='模型文件', blank=False)
    name = models.CharField(verbose_name='模型名称', max_length=16, blank=False)
    version = models.CharField(verbose_name='版本号', max_length=16, blank=True, default='v1.0')
    # args = models.CharField() Sklearn好像不支持额外参数

    class Meta:
        verbose_name = '模型'
        verbose_name_plural = '模型'
        unique_together = ('name', 'version') # 多字段联合的唯一性约束
