from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from xgame.models import *
from django.views import View
import json
import random
from .Consts import Vars
from django.utils import timezone


class VersionControl(View, Vars):
    def get(self, request):
        res = {'version': self.version, 'minVersion': self.min_version}
        return JsonResponse(res)


class Login(View):
    def post(self, request):
        data = json.loads(request.body)
        phone = data['phone']
        device_id = request.META.get('HTTP_DEVICE_ID')
        uwdi = User.objects.filter(device_id=device_id).exists()
        uwp = User.objects.filter(phone=phone).exists()
        try:
            if uwdi or uwp:
                user = User.objects.get(device_id=device_id) if uwdi else User.objects.get(phone=phone)
                user.activation_code = random.randint(100000, 999999)
                user.activation_expire = timezone.now() + timezone.timedelta(minutes=60)
                user.phone = phone
                user.device_id = device_id
                user.save()
                # for development
                code = user.activation_code
            else:
                user = User(phone=phone,
                            device_id=device_id,
                            activation_code=random.randint(100000, 999999),
                            activation_expire=timezone.now() + timezone.timedelta(minutes=60))
                user.save()
                # for development
                code = user.activation_code
            res = {'message': code}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class Activate(View, Vars):
    response = {'firstName': '', 'lastName': '', 'email': '', 'phone': '',
                'platform': '', 'accessToken': '', 'refreshToken': ''}

    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        try:
            data = json.loads(request.body)
            code = data['activationCode']
            user = get_object_or_404(User.objects.filter(activation_code=code, device_id=device_id,
                                                         activation_expire__gt=timezone.now()))
            if user.is_active:
                self.generate_token(user.id)
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.save()
                response = {'firstName': user.first_name, 'lastName': user.last_name, 'email': user.email,
                            'phone': user.phone, 'platform': user.platform, 'accessToken': user.access_token,
                            'refreshToken': user.refresh_token}
                return JsonResponse(response)
            else:
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.save()
                return JsonResponse(self.response, status=201)

        except Exception as e:
            print(e)
            return HttpResponse(e, status=403)


class Signup(View, Vars):
    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        data = json.loads(request.body)
        user = get_object_or_404(User.objects.filter(device_id=device_id))
        try:
            user.first_name = data['fName']
            user.last_name = data['lName']
            user.email = data['email']
            user.platform_id = data['platform']
            user.save()
            self.generate_token(user.id)
            res = {'name': user.first_name, 'lastName': user.last_name, 'email': user.email, 'phone': user.phone,
                   'platform': user.platform, 'accessToken': user.access_token,
                   'refreshToken': user.refresh_token}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)
