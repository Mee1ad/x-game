from xgame.models import User
from django.utils import timezone
import os
from django.conf import settings
from time import sleep
from xgame.urls import required_auth
from django.urls import resolve
from django.http import JsonResponse
import dataset
from xgame.views.Consts import Language


class AuthMiddleware(Language):
    def __init__(self, get_response):
        super().__init__()
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        app_name = resolve(request.path_info).app_name
        if app_name == 'admin' or 'jet' and app_name != '':
            response = self.get_response(request)
            return response
        ip = request.META['REMOTE_ADDR']
        filename = os.path.join(settings.BASE_DIR + '/logs/info', 'info.log')
        file = open(filename, "a")
        file.write(ip + ' - ')
        file.close()
        device_id = request.META.get('HTTP_DEVICE_ID')
        access_token = request.META.get('HTTP_ACCESS_TOKEN')
        refresh_token = request.META.get('HTTP_REFRESH_TOKEN')
        lang = request.META.get('HTTP_LANGUAGE')
        user_agent = request.META.get('HTTP_OS')
        # print('TCL: ', request.META.get('HTTP_TCL'))
        # print('VCL: ', request.META.get('HTTP_VCL'))
        # print('VCL2: ', request.META.get('HTTP_VCL2'))
        def f(x):
            return {
                'en': self.en,
                'fa': self.fa,
            }[x]
        try:
            request.response = f(lang)
        except Exception:
            request.response = self.en
        user_exist = User.objects.filter(device_id=device_id, refresh_token=refresh_token,
                                         refresh_token_expire__gte=timezone.now(), is_active=1).exists()
        if user_exist:
            user = User.objects.get(device_id=device_id, refresh_token=refresh_token,
                                    refresh_token_expire__gte=timezone.now(), is_active=1)
            request.user = user
            response = self.get_response(request)
            return response
        user_exist = User.objects.filter(device_id=device_id, access_token=access_token,
                                         access_token_expire__gte=timezone.now(), is_active=1).exists()

        if user_exist:
            user = User.objects.get(device_id=device_id, access_token=access_token,
                                    access_token_expire__gte=timezone.now(), is_active=1)
            request.user = user
        else:
            request.user = "guest"
            # BruteForce.check_ip_user(request, current_url, ip, 4, 1)
            current_url = resolve(request.path_info).url_name
            if current_url in required_auth:
                return JsonResponse({"message": "Unauthorized"}, status=401)

        response = self.get_response(request)
        sleep(.5)
        # Code to be executed for each request/response after
        # the view is called.

        return response
