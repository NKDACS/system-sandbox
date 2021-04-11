from django.contrib import admin, messages
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models.query import QuerySet
from .models import MyUser, Resume, ResumeResult, Announcement, MLModel


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
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    delete_old.short_description = '删除选中账号中所有一年以前注册的'

    def set_teacher(self, request, queryset: QuerySet):
        # 自动建立教师和学生两个用户组
        if not Group.objects.filter(name='teacher').exists():
            teacher = Group.objects.create(name='teacher')
            teacher.permissions.add(
                Permission.objects.get(codename='polls.view_MyUser'),
                Permission.object.get(codename='polls.view_Resume'),
                Permission.object.get(codename='polls.change_Resume'),
                Permission.object.get(codename='polls.view_Announcement'),
                Permission.object.get(codename='polls.add_Announcement'),
                Permission.object.get(codename='polls.delete_Announcement'),
                Permission.object.get(codename='polls.view_ResumeResult'),
                Permission.object.get(codename='polls.change_ResumeResult'),
            )
            teacher.save()
        try:
            for obj in queryset:
                obj.groups.set([Group.objects.get(name='teacher')])
                obj.is_staff = True
                obj.save()
            self.message_user(request, '将{}个账号变更为教师'.format(queryset.count()), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    set_teacher.short_description = '将选中账号设为教师'

    def set_student(self, request, queryset):
        if not Group.objects.filter(name='student').exists():
            student = Group.objects.create(name='student')
            student.permissions.set([])
            student.save()
        try:
            for obj in queryset:
                obj.groups.set([Group.objects.get(name='student')])
                obj.is_staff = False
                obj.save()
            self.message_user(request, '将{}个账号变更为学生'.format(queryset.count()), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    set_student.short_description = '将选中账号设为学生'

    actions = [delete_old, set_teacher, set_student]


class ResumeResultInline(admin.TabularInline):
    model = ResumeResult


class ResumeAdmin(ModelAdmin):
    list_display = (
        '__str__', 
        'name_display', 'id_display', 'email_display', 'phone_display', 
        'university', 'submitted', 'special_permit', 'admiss_display')

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

    def admiss_display(self, obj):
        return ResumeResult.objects.get(resume=obj).admiss
    admiss_display.short_description = '录取'

    def reject(self, request, queryset: QuerySet):
        try:
            num = queryset.update(special_permit=True, submitted=False)
            self.message_user(
                request, '{}份简历打回成功'.format(num), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    reject.short_description = '将选中简历打回修改'

    def admiss(self, request, queryset: QuerySet):
        try:
            for obj in queryset:
                r = ResumeResult.objects.get(resume=obj)
                r.admiss = True
                r.save()
            self.message_user(
                request, '将{}份简历设为录取'.format(queryset.count()), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    admiss.short_description = '将选中考生设为录取'

    def admiss_reverse(self, request, queryset: QuerySet):
        try:
            for obj in queryset:
                r = ResumeResult.objects.get(resume=obj)
                r.admiss = False
                r.save()
            self.message_user(
                request, '将{}份简历取消录取'.format(queryset.count()), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, e.__str__(), messages.ERROR)
    admiss_reverse.short_description = '将选中考生取消录取'

    actions = [reject, admiss, admiss_reverse]
    inlines = [ResumeResultInline]


# 将模型注册到后台
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Resume, ResumeAdmin)
admin.site.register([Announcement, ResumeResult, MLModel])
