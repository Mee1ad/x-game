from django.core.files.temp import NamedTemporaryFile
from django.utils.timezone import activate
from django.core import serializers
from django.utils import timezone
from GameExchange import settings
from django.views import View
from secrets import token_hex
from xgame.models import *
import requests
import ast
import threading
import dataset
import os
from django.http import JsonResponse
import re


activate(settings.TIME_ZONE)


class Language:
    def __init__(self):
        self.en = {'add_review': "Comment Successfully Added", 'add_sell': 'Uploaded Successfully',
                   'login': 'Login Successfully', 'invalid': 'is invalid',
                   'activate_new_user': 'Please Fill Data To Complete Your Signup Process', 'wrong_code': 'Code Not Found',
                   '401': 'Unauthenticated', 'logout': 'successfully signed out'}
        self.fa = {'add_review': "نقد شما ذخیره شد", 'add_sell': 'بازی به فروشگاه اضافه شد', 'login': 'خوش آمدید',
                   'activate_new_user': 'برای کامل کردن ثبت نام لصفا فرم را پر کنید', 'wrong_code': 'کد فعالسازی اشتباه است',
                   '401': 'کاربر نامعتبر میباشد', 'logout': 'خروج موفق', 'invalid': 'نامعتبر است'}


class Vars(View):
    version = 1
    min_version = 1
    link = ''
    platform = {0: 'nothing', 1: 'PlayStation 4', 2: 'Xbox One', 3: 'nintendo switch', 4: 'PC (Microsoft Windows)'}
    media_type = {0: 'cover', 1: 'screenshot', 2: 'trailer', 3: 'seller_photos'}
    ten_days_later = timezone.now() + timezone.timedelta(days=10)
    base_url = 'https://api-v3.igdb.com'
    api_key = 'b2ca5a63f6073504b735c49435f69cee'
    image_url = 'https://images.igdb.com/igdb/image/upload/t_720p/'
    screenshot = 'https://images.igdb.com/igdb/image/upload/t_screenshot_big/'
    cover = 'https://images.igdb.com/igdb/image/upload/t_720p/'
    media = 'http://192.168.1.95'
    # media = 'XGame.pythonanywhere.com'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                 ' Chrome/72.0.3626.119 Safari/537.36'
    threadLock = threading.Lock()
    threads = []

    def generate_token(self, user_id):
        user = User.objects.get(pk=user_id)
        user.access_token = token_hex(511)
        user.refresh_token = token_hex(511)
        user.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        user.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
        user.save()
        return {'access_token': user.access_token, 'refresh_token': user.refresh_token}

    def string_to_list(self, string):
        s = serializers.serialize("json", string)
        s = s.replace('false', 'False').replace('true', 'True').replace('null', 'None')
        s = ast.literal_eval(s)
        if s:
            for obj in s:
                obj['fields']['id'] = obj['pk']
            if 'price' in s[0]['fields']:
                for obj in s:
                    price = obj['fields']['price']
                    if price < 1000000:
                        obj['fields']['price'] = f"{int(price / 1000)}K"
                    else:
                        obj['fields']['price'] = f"{int(price / 1000000) if price % 1000000 == 0 else price / 1000000}M"

            if 'created_at' in s[0]['fields']:
                for obj in s:
                    obj['fields']['created_at'] = self.datetime_serializer(obj['fields']['created_at'])
                    obj['fields']['updated_at'] = self.datetime_serializer(obj['fields']['updated_at'])
        return s

    def datetime_serializer(self, time):
        time = time.replace('T', ', ')
        time = time.split('.')[0]
        return time

    def file_cache(self, url):
        r = requests.get(url)
        img_temp = NamedTemporaryFile()
        img_temp.write(r.content)
        img_temp.flush()
        return img_temp


class Validation(View):

    def __init__(self):
        super().__init__()
        self.game_name_pattern = r'^\w+\d*$'
        self.name_pattern = r'^([a-z آ-ی 0-9]+)$'
        self.phone_pattern = r'^(09[0-9]{9})$'
        self.activation_code_pattern = r'^\d{6}$'
        self.email_pattern = r'^\w+.*-*@\w+.com$'
        self.platform_pattern = r'^[0-4]$'
        self.text = r'^[\w\d;\[\]!?+=()%.]+$'
        self.id = r'^\d+$'
        self.rate = r'^[0-9]$|10'

    def validation(self, pattern, text):
        def f(x):
            return {
                'game_name': self.game_name_pattern,
                'name': self.name_pattern,
                'phone': self.phone_pattern,
                'activation_code': self.activation_code_pattern,
                'email': self.email_pattern,
                'platform': self.platform_pattern,
                'text': self.text,
                'id': self.id,
                'rate': self.rate,
            }[x]
        valid = re.search(f(pattern), f'{text}')
        if valid:
            return valid[0]
        return 'no match'


class BruteForce(View):
    @staticmethod
    def check_ip_user(request, current_url, ip, rate, time):
        db = dataset.connect('sqlite:///cache.db')
        table = db['ip']
        filename = os.path.join(settings.BASE_DIR + '/logs', 'brute_force.log')
        file = open(filename, "a")
        file.write(ip + ' - ')
        file.close()
        restrict_ip = table.find_one(ip=ip)
        if restrict_ip is not None and timezone.now() < restrict_ip['time']:
            return JsonResponse({'message': 'restricted'})
        elif restrict_ip is not None and timezone.now() > restrict_ip['time']:
            table.delete(ip=restrict_ip['ip'])
        table = db['ip']
        first = table.find_one(id=1)
        if first is not None and first['ip'] != ip and first['user'] != request.user:
            table.update(dict(id=1, ip=ip, time=timezone.now(), user=request.user, route=current_url), ['id'])
            table.delete(ip=first['ip'])
        elif first is None or first['ip'] == ip or first['user'] == request.user:
            table.insert(dict(ip=ip, time=timezone.now(), user=request.user, route=current_url))
            ip_retry = table.find(ip=ip)
            user_retry = table.find(user=request.user)
            i, j = 0, 0
            for item in ip_retry:
                i += 1
            for item in user_retry:
                j += 1
            if i > rate or j > rate and (first['time'] + timezone.timedelta(minutes=time) > timezone.now()):
                table = db['restrict']
                table.insert(dict(ip=ip, user=request.user, time=timezone.now() + timezone.timedelta(minutes=time)))
                table.delete(ip=first['ip'])
