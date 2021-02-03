from django.contrib import admin, messages
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models.query import QuerySet
from .models import *


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name',
                             'email', 'number', 'phone', 'person_id')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'person_id', 'is_active', 'is_staff', 'date_joined')

    def delete_old(self, request, queryset: QuerySet):
        from django.utils.timezone import now
        try:
            num = queryset.filter(date_joined__lte=now().replace(
                year=now().year-1)).delete()
            self.message_user(request, '{}个过期账号删除成功'.format(num), messages.SUCCESS)
        except:
            self.message_user(request, '错误：删除失败', messages.ERROR)
    delete_old.short_description = '删除选中账号中所有一年以前注册的'

    def set_teacher(self, request, queryset: QuerySet):
        try:
            for obj in queryset:
                obj.groups.set([Group.objects.get(name='teacher')])
                obj.is_staff = True
                obj.save()
            self.message_user(request, '将{}个账号变更为教师'.format(queryset.count()), messages.SUCCESS)
        except:
            self.message_user(request, '错误：变更失败', messages.ERROR)
    set_teacher.short_description = '将选中账号设为教师'

    def set_student(self, request, queryset):
        try:
            for obj in queryset:
                obj.groups.set([Group.objects.get(name='student')])
                obj.is_staff = False
                obj.save()
            self.message_user(request, '将{}个账号变更为学生'.format(queryset.count()), messages.SUCCESS)
        except:
            self.message_user(request, '错误：变更失败', messages.ERROR)
    set_student.short_description = '将选中账号设为学生'

    actions = [delete_old, set_teacher, set_student]


class ResumeAdmin(ModelAdmin):
    list_display = (
        '__str__', 
        'name_display', 'id_display', 'email_display', 'phone_display', 
        'university', 'submitted')

    def name_display(self, obj):
        return (obj.student.last_name or '') + (obj.student.first_name or '')
    name_display.short_description = '姓名'

    def id_display(self, obj):
        return obj.student.person_id
    id_display.short_description = '身份证号'

    def email_display(self, obj):
        return obj.student.email
    email_display.short_description = '邮箱'

    def phone_display(self, obj):
        return obj.student.phone
    phone_display.short_description = '手机'
    
    


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register([Anoucement])

if not Group.objects.filter(name='teacher').exists():
    teacher = Group.objects.create(name='teacher')
    teacher.permissions.add(
        Permission.objects.get(codename='polls.view_MyUser'),
        Permission.object.get(codename='polls.view_Resume'),
        Permission.object.get(codename='polls.view_Anouncement'),
        Permission.object.get(codename='polls.add_Anouncement'),
        Permission.object.get(codename='polls.delete_Anouncement'),
        Permission.object.get(codename='polls.change_Anouncement'),
    )
    teacher.save()

if not Group.objects.filter(name='student').exists():
    student = Group.objects.create(name='student')
    student.permissions.set([])
    student.save()
