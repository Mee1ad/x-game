from django.shortcuts import get_object_or_404
from xgame.decorators import try_except
from django.http import JsonResponse
from django.utils import timezone
from xgame.models import *
from .Consts import Vars
import random
import json


class VersionControl(Vars):
    @try_except
    def get(self, request):
        res = {'version': self.version, 'min_version': self.min_version}
        return JsonResponse(res)


class Login(Vars):
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        phone = data['phone']
        device_id = request.META.get('HTTP_DEVICE_ID')
        uwdi = User.objects.filter(device_id=device_id).exists()
        uwp = User.objects.filter(phone=phone).exists()
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


class Activate(Vars):
    response = {'firstName': '', 'lastName': '', 'email': '', 'phone': '',
                'platform': '', 'accessToken': '', 'refreshToken': ''}

    @try_except
    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        data = json.loads(request.body)
        code = data['activationCode']
        user_exists = User.objects.filter(activation_code=code, device_id=device_id,
                                          activation_expire__gte=timezone.now()).exists()
        if user_exists:
            user = User.objects.get(activation_code=code, device_id=device_id,
                                    activation_expire__gte=timezone.now())
            if user.is_active:
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.save()
                self.generate_token(user.id)
                user = User.objects.get(device_id=device_id)
                response = {'firstName': user.first_name, 'lastName': user.last_name, 'email': user.email,
                            'phone': user.phone, 'platform': user.platform, 'accessToken': user.access_token,
                            'refreshToken': user.refresh_token}
                return JsonResponse(response)
            else:
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.save()
                return JsonResponse(self.response, status=201)
        else:
            res = {"message": "Code Not Found"}
            return JsonResponse(res, status=404)


class Signup(Vars):
    @try_except
    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        data = json.loads(request.body)
        user = get_object_or_404(User, device_id=device_id)
        user.first_name = data['fName']
        user.last_name = data['lName']
        user.email = data['email']
        user.platform = data['platform']
        user.is_active = True
        user.save()
        self.generate_token(user.id)
        user = User.objects.get(device_id=device_id)
        res = {'name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'phone': user.phone,
               'platform': user.platform, 'access_token': user.access_token,
               'refresh_token': user.refresh_token}
        return JsonResponse(res)

