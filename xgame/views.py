from django.views.decorators.http import require_POST, require_safe
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Exists
from secrets import token_hex
from .models import *
import json
import random


@require_POST
def signup(request):
    data = json.loads(request.body)
    phone = data['phone']
    device_id = request.META.get('HTTP_DEVICE_ID')
    temp_user = UserTemp.objects.filter(device_id=device_id).exists()
    if temp_user:
        temp_user = UserTemp.objects.get(device_id=device_id)
        temp_user.activation_code = random.randint(100000, 999999)
        temp_user.phone = phone
        temp_user.expire_date = timezone.now() + timezone.timedelta(minutes=60)
        temp_user.save()
    else:
        print(2)
        user = UserTemp(phone=phone,
                        device_id=device_id,
                        activation_code=random.randint(100000, 999999),
                        expire_date=timezone.now() + timezone.timedelta(minutes=60))
        user.save()
    res = {'message': 'Signup Successfully'}
    return JsonResponse(res)


@require_safe
def activate(request):
    device_id = request.META.get('HTTP_DEVICE_ID')
    try:
        code = request.GET.get('activation_code', '')
        temp_user_exist = UserTemp.objects.filter(activation_code=code).exists()
        if temp_user_exist:
            user_exist = User.objects.filter(device_id=device_id).exists()
            if user_exist:
                user = User.objects.get(device_id=device_id)
                generate_token(user.id)
                tokens = Token.objects.get(user_id=user.id)
                tokens = json.loads(f"{tokens}")
                temp_user = UserTemp.objects.get(activation_code=code)
                temp_user.delete()
                return JsonResponse(tokens)
            else:
                temp_user = UserTemp.objects.get(activation_code=code)
                new_user = User(phone=temp_user.phone, device_id=device_id)
                new_user.save()
                temp_user.delete()
                res = {'message': 'Activate Successfully'}
                return JsonResponse(res)
        else:
            res = {'message': 'Activate failed'}
            return JsonResponse(res)
    except ObjectDoesNotExist:
        res = {'message': 'Activate failed'}
        return JsonResponse(res)


@require_POST
def profile(request):
    device_id = request.META.get('HTTP_DEVICE_ID')
    data = json.loads(request.body)
    user_exist = User.objects.filter(device_id=device_id).exists()
    if user_exist():
        user = User.objects.get(device_id=device_id)
        user.username = data['username']
        user.email = data['email']
        user.password = data['password']
        user.console = data['console']
        user.save()
        generate_token(user.id)
        tokens = Token.objects.get(user_id=user.id)
        tokens = json.loads(f"{tokens}")
        return JsonResponse(tokens)
    else:
        res = {'message': "User Does Not Exist"}
        return JsonResponse(res)


def generate_token(user_id):
    tokens = Token.objects.filter(user_id=user_id)
    if tokens is None:
        tokens = Token(access_token=token_hex(1023), refresh_token=token_hex(1023), user_id=user_id)
        tokens.save()
    else:
        tokens.access_token = token_hex(1023)
        tokens.refresh_token = token_hex(1023)
        tokens.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        tokens.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
