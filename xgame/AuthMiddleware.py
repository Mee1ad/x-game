from xgame.models import *
from django.utils import timezone
import os
from django.conf import settings


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        ip = request.META['REMOTE_ADDR']
        filename = os.path.join(settings.BASE_DIR + '/logs/info', 'info.log')
        file = open(filename, "a")
        file.write(ip + ' - ')
        file.close()
        device_id = request.META.get('HTTP_DEVICE_ID')
        access_token = request.META.get('HTTP_ACCESS_TOKEN')
        user_exist = User.objects.filter(device_id=device_id, access_token=access_token,
                                         access_token_expire__gte=timezone.now(), is_active=1).exists()
        request.user = "guest"
        if user_exist:
            user = User.objects.get(device_id=device_id, access_token=access_token,
                                    access_token_expire__gte=timezone.now(), is_active=1)
            request.user = user

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
