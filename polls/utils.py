from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (str(user.pk) + str(timestamp) + str(user.is_active))


account_activation_token = TokenGenerator()

def send_activate_email(request, user):
    mail_content = render_to_string('polls/account_activate_email.html', {
        'first': user.first_name,
        'last': user.last_name,
        'user': user.username,
        'domain': get_current_site(request) .domain,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': account_activation_token.make_token(user),
    })
    send_mail(
        '激活账号 - 南开大学统计与数据科学学院研究生推免报名系统', 
        mail_content, 
        settings.EMAIL_HOST_USER, 
        [user.email]
    )

def IDValidator(value):
    #身份证号码验证
    Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    Ti = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    sum = 0
    #身份证第十八位可能是X，输入时将小写x转换为大写X
    value = value.upper()
    if len(value) != 18:
         raise ValueError('请输入18位身份证号码,您只输入了%s位' % len(value))
    for i in range(17):
        sum += int(value[i]) * Wi[i]
    if Ti[sum % 11] != value[17]:
        raise ValueError('请输入正确的身份证号码')


class GlobalVar(object):
    from django.core.cache import cache

    @staticmethod
    def get():
        pass


def get_university():
    result = finders.find('ChinaUniversityList.json')
    from json import load
    file = open(result, 'r', encoding='utf-8')
    d = load(file)
    school = []
    for i in d:
        local_school = [(j['code'], j['name']) for j in i['schools']]
        school.append((i['province'], local_school))
    return school

UNIVERSITY = get_university()


def check_resume(resume):
    """
    这里定义简历字段逻辑，用于检验
    """
    errors = []
    validator = {
        'university': [(lambda x: x.university == '', '为空')],
        'major_student_amount': [
            (lambda x: x.major_student_amount == 0, '为0'),
            (lambda x: x.major_student_amount < x.rank, '小于个人排名')
        ],
        'gpa': [(lambda x: x.gpa>100, '大于100')]
    }
    for f in resume.__dict__.keys():
        if f in validator.keys():
            for v in validator[f]:
                try:
                    if v[0](resume):
                        errors.append({'name': f, 'msg': '不能'+v[1]})
                        break
                except:
                    errors.append({'name': f, 'msg': '不能为空'})
                    break
    return errors


def check_deadline_pass():
    # TODO: 实现检测是否过了deadline的工具函数
    return False
