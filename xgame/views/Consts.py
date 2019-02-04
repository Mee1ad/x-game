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

activate(settings.TIME_ZONE)


class Vars(View):
    version = 2.3
    min_version = 2.1
    platform = {0: 'nothing', 1: 'PlayStation 4', 2: 'Xbox One', 3: 'nintendo switch', 4: 'PC (Microsoft Windows)'}
    media_type = {0: 'cover', 1: 'screenshot', 2: 'trailer', 3: 'seller_photos'}
    ten_days_later = timezone.now() + timezone.timedelta(days=10)
    base_url = 'https://api-v3.igdb.com'
    battuta = 'https://battuta.medunes.net/api'
    api_key = '5e69676036907c1ee9c1b528f87ba11e'
    battuta_key = 'c72f083085065dc22df336021f7135bb'
    image_url = 'https://images.igdb.com/igdb/image/upload/t_720p/'
    screenshot = 'https://images.igdb.com/igdb/image/upload/t_screenshot_big/'
    cover = 'https://images.igdb.com/igdb/image/upload/t_cover_big/'
    media = 'localhost'

    def generate_token(self, user_id):
        user = User.objects.get(pk=user_id)
        user.access_token = token_hex(511)
        user.refresh_token = token_hex(511)
        user.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        user.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
        user.save()

    def string_to_list(self, string):
        s = serializers.serialize("json", string)
        s = s.replace('false', 'False').replace('true', 'True').replace('null', 'None')
        s = ast.literal_eval(s)
        if s:
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
