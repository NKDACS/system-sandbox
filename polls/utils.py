from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (str(user.pk) + str(timestamp) + str(user.is_active))


account_activation_token = TokenGenerator()

def send_activate_email(request, user):
    mail_content = render_to_string('email_template.html', {
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
        settings.EMAIL_HOST, 
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
