from django.shortcuts import get_object_or_404
from xgame.decorators import try_except
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from xgame.models import *
from .Consts import Vars, Validation
from .api import GameDetail
import random
import json
from fcm_django.models import FCMDevice


class Test(Validation):
    @try_except
    def put(self, request):
        device = FCMDevice.objects.get(pk=10)
        res = {'min_version': 'pashamak'}
        return JsonResponse(res)


class VersionControl(Vars):
    @try_except
    def get(self, request):
        res = {'version': self.version, 'min_version': self.min_version, 'link': self.link}
        return JsonResponse(res)


class Login(Vars, Validation):
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        valid = {'phone': self.validation('phone', data['phone'])}
        for key, value in valid.items():
            if "no match" in value:
                # return JsonResponse({'message': f'{key} ' + request.response['invalid']}, status=406)
                return JsonResponse({'message': f'{key} ' + request.response['invalid']}, status=406)
        phone = valid['phone']
        device_id = request.META.get('HTTP_DEVICE_ID')
        uwp = User.objects.filter(phone=phone).exists()
        if uwp:
            user = User.objects.get(phone=phone)
            user.activation_code = random.randint(100000, 999999)
            user.activation_expire = timezone.now() + timezone.timedelta(minutes=60)
            user.save()
            device = FCMDevice.objects.get(user_id=user.id)
            device.device_id = device_id
            device.save()
            # for development
            code = user.activation_code
        else:
            user = User(phone=phone,
                        device_id=device_id,
                        activation_code=random.randint(100000, 999999),
                        activation_expire=timezone.now() + timezone.timedelta(minutes=60))
            user.save()
            device = FCMDevice(device_id=device_id,
                               user_id=user.id,
                               type="android")
            device.save()
            # for development
            code = user.activation_code
        res = {'message': code}
        return JsonResponse(res)


class Activate(GameDetail, Validation):
    response = {'new_user': True,
                'fName': '', 'lName': '', 'email': '', 'phone': '',
                'platform': 0, 'access_token': '', 'refresh_token': ''}

    @try_except
    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        data = json.loads(request.body)
        valid = {'code': self.validation('activation_code', data['activation_code'])}
        for key, value in valid.items():
            if "no match" in value:
                return JsonResponse({'message': f'{key} ' + request.response['invalid']}, status=406)
        code = valid['code']
        firebase_id = data['tf']
        user_exists = User.objects.filter(activation_code=code, activation_expire__gte=timezone.now()).exists()
        if user_exists:
            user = User.objects.get(activation_code=code, activation_expire__gte=timezone.now())
            duplicate_device = FCMDevice.objects.filter(device_id=device_id, active=True).exists()
            if duplicate_device:
                device = FCMDevice.objects.get(device_id=device_id, active=True)
                device.active = False
                device.save()
            device = FCMDevice.objects.get(user_id=user.id)
            device.registration_id = firebase_id
            device.save()
            if user.is_active or user.access_token is not None:
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.device_id = device_id
                user.firebase_id = firebase_id
                user.is_active = True
                user.save()
                tokens = self.generate_token(user.id)
                user = User.objects.get(phone=user.phone)
                response = {'message': request.response['login'], 'new_user': False,
                            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,
                            'phone': user.phone, 'platform': user.platform, **tokens}
                return JsonResponse(response)
            else:
                user.activation_code = None
                user.activation_expire = timezone.now()
                user.save()
                self.response['message'] = request.response['activate_new_user']
                return JsonResponse(self.response)
        else:
            res = {"message": request.response['wrong_code']}
            return JsonResponse(res, status=400)


class Signup(Vars, Validation):
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        valid = {'phone': self.validation('phone', data['phone']),
                 'fName': self.validation('name', data['fName']),
                 'lName': self.validation('name', data['lName']),
                 'email': self.validation('email', data['email']),
                 'platform': self.validation('platform', data['platform'])}
        for key, value in valid.items():
            if "no match" in value:
                return JsonResponse({'message': f'{key} ' + request.response['invalid']}, status=406)
        phone = valid['phone']
        user_exists = User.objects.filter(phone=phone).exists()
        if user_exists:
            user = User.objects.get(phone=phone)
            device = FCMDevice.objects.get(user_id=user.id)
            device.active = True
            device.save()
            if user.access_token is not None and request.user != user:
                return JsonResponse({'message': request.response['401']}, status=401)
            user.first_name = valid['fName']
            user.last_name = valid['lName']
            user.email = valid['email']
            user.platform = valid['platform']
            user.username = valid['fName'] + valid['lName']
            user.is_active = True
            user.save()
            tokens = self.generate_token(user.id)
            user = User.objects.get(phone=phone)
            res = {'message': request.response['sign_up'], 'first_name': user.first_name, 'last_name': user.last_name,
                   'email': user.email, 'phone': user.phone, 'platform': user.platform, **tokens}
            return JsonResponse(res)
        else:
            return JsonResponse({'message': request.response['401']}, status=401)


class RefreshTokens(Vars):
    def get(self, request):
        res = self.generate_token(request.user.id)
        return JsonResponse(res)


class LogOut(Vars):
    def get(self, request):
        request.user.is_active = False
        request.user.access_token_expire = timezone.now()
        request.user.refresh_token_expire = timezone.now()
        request.user.save()
        return JsonResponse({'message': request.response['logout']})
