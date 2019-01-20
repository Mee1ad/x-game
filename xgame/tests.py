from django.test import TestCase
from django.contrib import auth
from .models import *


class Test(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('test', 'test@dom.com', 'sdgsd51g5sd1g')
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.is_active = True
        self.u.save()

    def testLogin(self):
        self.client.login(username='test', password='sdgsd51g5sd1g')
