from django.test import TestCase, client
from django.contrib.auth import get_user_model
from django.urls.base import reverse

User = get_user_model()

# Create your tests here.
class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        return super().setUpTestData()

    def test_registration(self):
        cli = client.Client()
        resp = cli.post(reverse('register'), {
            'username': 'a',
            'password1': 'a',
            'password2': 'a',
            'email': 'a@a.com',
            'last_name': 'a',
            'first_name': 'a',
            'person_id': 1,
            'phone': '11111111111',
        })
        # print(resp.content)
        self.assertContains(resp, '* person_id\n  *')