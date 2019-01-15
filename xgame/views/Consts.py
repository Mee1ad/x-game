from django.utils import timezone
from secrets import token_hex
from xgame.models import *


class Vars:
    version = 2.3
    min_version = 2.1
    platform = {0: 'nothing', 1: 'ps4', 2: 'xbox1', 3: 'nintendo switch', 4: 'pc'}
    media_type = {0: 'cover', 1: 'screenshot', 2: 'trailer', 3: 'seller_photos'}
    ten_days_later = default=timezone.now() + timezone.timedelta(days=10)

    def generate_token(self, user_id):
        user = User.objects.get(id=user_id)
        user.access_token = token_hex(511)
        user.refresh_token = token_hex(511)
        user.access_token_expire = timezone.now() + timezone.timedelta(days=10)
        user.refresh_token_expire = timezone.now() + timezone.timedelta(days=30)
        user.save()

