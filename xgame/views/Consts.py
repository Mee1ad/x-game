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

activate(settings.TIME_ZONE)


class Vars(View):
    version = 1
    min_version = 1
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
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    threadLock = threading.Lock()
    threads = []

    def generate_token(self, user_id):
        user = User.objects.get(pk=user_id)
        user.access_token = token_hex(511)
        user.refresh_token = token_hex(511)
        print('generated access:', user.access_token)
        print('generated refresh:', user.refresh_token)
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
