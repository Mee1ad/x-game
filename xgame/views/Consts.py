from django.utils import timezone
from secrets import token_hex
from xgame.models import *


class Vars:
    version = 2.3
    min_version = 2.1
    platform = {0: 'nothing', 1: 'PlayStation 4', 2: 'Xbox One', 3: 'nintendo switch', 4: 'PC (Microsoft Windows)'}
    media_type = {0: 'cover', 1: 'screenshot', 2: 'trailer', 3: 'seller_photos'}
    ten_days_later = default=timezone.now() + timezone.timedelta(days=10)
    base_url = 'https://api-v3.igdb.com'
    api_key = '5e69676036907c1ee9c1b528f87ba11e'
    image_url = 'https://images.igdb.com/igdb/image/upload/t_720p/'
    screenshot = 'https://images.igdb.com/igdb/image/upload/t_screenshot_big/'
    cover = 'https://images.igdb.com/igdb/image/upload/t_cover_big/'

    def generate_token(self, user_id):
        user = User.objects.get(id=user_id)
        user.access_token = token_hex(511)
        user.refresh_token = token_hex(511)
        user.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        user.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
        user.save()

