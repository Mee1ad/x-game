from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from secrets import token_hex
from xgame.models import *
from django.views import View
import json
import random


class VersionControl(View):
    pass


class Login(View):
    def post(self, request):
        data = json.loads(request.body)
        phone = data['phone']
        device_id = request.META.get('HTTP_DEVICE_ID')
        tuwdi = UserTemp.objects.filter(device_id=device_id).exists()
        tuwp = UserTemp.objects.filter(phone=phone).exists()
        try:
            if tuwdi or tuwp:
                temp_user = UserTemp.objects.get(device_id=device_id) if tuwdi else UserTemp.objects.get(phone=phone)
                temp_user.activation_code = random.randint(100000, 999999)
                temp_user.phone = phone
                temp_user.device_id = device_id
                temp_user.expire_date = timezone.now() + timezone.timedelta(minutes=60)
                temp_user.save()
                code = temp_user.activation_code
            else:
                user = UserTemp(phone=phone,
                                device_id=device_id,
                                activation_code=random.randint(100000, 999999),
                                expire_date=timezone.now() + timezone.timedelta(minutes=60))
                user.save()
                code = user.activation_code
            res = {'message': code}
            return JsonResponse(res)
        except Exception as e:
            res = {'message': e}
            return JsonResponse(res)


class Activate(View):
    res = {'username': '', 'photo': '', 'email': '', 'phone': '',
           'platform': '', 'accessToken': '', 'refreshToken': ''}

    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        try:
            data = json.loads(request.body)
            code = data['activationCode']
            temp_user = get_object_or_404(UserTemp.objects.filter(activation_code=code, expire_date__gt=timezone.now()))
            phone = temp_user.phone
            uewd = User.objects.filter(device_id=device_id).exists()
            uewp = User.objects.filter(phone=phone).exists()
            if uewd or uewp:
                user = User.objects.get(device_id=device_id) if uewd else User.objects.get(phone=phone)
                user.device_id = device_id
                user.save()
                token_exist = Token.objects.filter(user_id=user.id).exists()
                if token_exist:
                    generate_token(user.id)
                    tokens = Token.objects.get(user_id=user.id)
                    temp_user = UserTemp.objects.get(activation_code=code)
                    temp_user.delete()
                    res = {'username': user.username, 'photo': user.photo, 'email': user.email, 'phone': user.phone,
                           'platform': user.platform,'accessToken': tokens.access_token,
                           'refreshToken': tokens.refresh_token}
                    return JsonResponse(res)
                else:
                    temp_user.delete()
                    return JsonResponse(self.res, status=201)
            else:
                new_user = User(phone=temp_user.phone, device_id=device_id)
                new_user.save()
                temp_user.delete()
                return JsonResponse(self.res, status=201)
        except IntegrityError as e:
            print(e)
            res = {'message': 'Duplicate Error'}
            return JsonResponse(res)


class Signup(View):
    def post(self, request):
        device_id = request.META.get('HTTP_DEVICE_ID')
        security_code = request.META.get('HTTP_SECURITY_CODE')
        data = json.loads(request.body)
        user = get_object_or_404(User.objects.filter(device_id=device_id))
        if security_code == user.device_id + 'm':
            try:
                user.first_name = data['fName']
                user.last_name = data['lName']
                user.email = data['email']
                user.platform_id = data['platform']
                user.save()
                generate_token(user.id)
                tokens = Token.objects.get(user_id=user.id)
                res = {'name': user.first_name, 'lastName': user.last_name, 'email': user.email, 'phone': user.phone,
                       'platform': user.platform_id, 'accessToken': tokens.access_token,
                       'refreshToken': tokens.refresh_token}
                return JsonResponse(res)
            except IntegrityError:
                res = {'message': "Duplicate Username"}
                return JsonResponse(res, status=406)
        else:
            res = {'message': "Access Denied"}
            return JsonResponse(res, status=403)


def generate_token(user_id):
    tokens = Token.objects.filter(user_id=user_id).exists()
    if tokens:
        tokens = Token.objects.get(user_id=user_id)
        tokens.access_token = token_hex(1023)
        tokens.refresh_token = token_hex(1023)
        tokens.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        tokens.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
        tokens.save()
    else:
        tokens = Token(access_token=token_hex(1023), refresh_token=token_hex(1023), user_id=user_id)
        tokens.save()

