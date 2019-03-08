from .views.Consts import Vars
from django.http import JsonResponse, HttpResponse
import threading
import requests
from xgame.decorators import try_except
from django.core.files import File
from xgame.models import *


class Aparat:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
               'Content-Type': 'application/json;charset=UTF-8', 'host': 'api.aparat.com', 'Origin': 'https://www.aparat.com'}
    user = "sjdfnskjfkskf"
    password = "19951374"
    all_aparat_link = []

    def signin(self):
        url = 'https://api.aparat.com/fa/v1/user/account/signin/'
        self.headers['Referer'] = 'https://www.aparat.com/authentication'
        self.headers['Access-Control-Request-Method'] = 'POST'
        self.headers['Access-Control-Request-Headers'] = 'content-type,x-sabaenv'
        data = {"account": self.user}
        r = requests.options(url, headers=self.headers)
        self.headers['X-SabaENV'] = "{}"
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code == 200:
            temp_id = r.json()['data']['attributes']['tempId']
            return self.signin_password(temp_id)
        else:
            print(r.status_code)
            print(r.json())
            return HttpResponse("signin error")

    def signin_password(self, temp_id):
        url = 'https://api.aparat.com/fa/v1/user/account/signin_password'
        self.headers['Referer'] = 'https://www.aparat.com/authentication/signin/password'
        self.headers['X-SabaENV'] = '{}'
        data = {"account": self.user, "password": self.password, "tempId": temp_id}
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code == 200:
            token = r.json()['data']['attributes']['token']
            for link in self.links:
                l = self.upload_form(token, link)
                self.all_aparat_link.append(l)
        else:
            print("signin_password error")
            return HttpResponse("signin_password error")

    def upload_form(self, token, youtube_link):
        url = 'https://api.aparat.com/fa/v1/video/upload/url/'
        self.headers['Referer'] = 'https://www.aparat.com/uploadnew'
        self.headers['Access-Control-Request-Headers'] = 'Access-Control-Request-Headers'
        self.headers['Access-Control-Request-Method'] = 'POST'
        self.headers['Authorization'] = f'Bearer {token}'
        data = {"url": youtube_link}
        r = requests.options(url, headers=self.headers)
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        if r.status_code == 200:
            res = r.json()
            res = res['data']['attributes']
            video_id = res['id']
            upload_id = res['uploadId']
            title = res['title']
            tags = res['tags']
            youtube_url = res['url']
            return self.upload(upload_id, video_id, tags, title, youtube_url)
        else:
            print("upload_form error")
            return HttpResponse("upload_form error")

    def upload(self, upload_id, video_id, tags, title, youtube_url):
        url = f'https://api.aparat.com/fa/v1/video/upload/upload/uploadId/{upload_id}'
        self.headers['Access-Control-Request-Headers'] = 'authorization,content-type,x-requested-with'
        # del self.headers['X-SabaENV']
        data = {
            "category": "22",
            "comment": "no",
            "d360": "0",
            "descr": "",
            "id": video_id,
            "new_cat": "",
            "new_playlist": "",
            "playlistid": "",
            "profile_cat": "",
            "subtitle": "",
            "tags": " ".join(str(x) for x in tags) if tags else title,
            "title": title if len(title) <= 80 else title[:80],
            "uploadId": upload_id,
            "url": youtube_url,
            "video_pass": "",
            "watermark": "false"
        }
        r = requests.options(url, headers=self.headers)
        r = requests.post(url=url, data=json.dumps(data), headers=self.headers)
        if r.status_code == 200:
            link = 'https://aparat.com/v/' + r.json()['data']['attributes']['uid']
            return link
        else:
            print("upload error")
            return HttpResponse("upload error")


class UploadVideo(threading.Thread, Vars, Aparat):
    def __init__(self, links):
        threading.Thread.__init__(self)
        self.links = links

    def run(self):
        print('videos:', self.links)
        self.signin()
        print(self.all_aparat_link)
        print("videos uploaded")
        return "videos uploaded"


class UploadScreen(threading.Thread, Vars, Aparat):
    def __init__(self, url, game_id=0, game_name=""):
        threading.Thread.__init__(self)
        self.url = url
        self.game_id = game_id
        self.game_name = game_name

    def run(self):
        print('screenshots:', self.url)
        for url in self.url:
            img = self.file_cache(url)
            media = Media(table_id=self.game_id, type=1)
            media.screenshot.save(self.game_name + '.jpg', File(img), save=True)
        print("screenshots uploaded")
        return "screenshots uploaded"


class UploadCover(threading.Thread, Vars, Aparat):
    def __init__(self, url, game_id=0, game_name=""):
        threading.Thread.__init__(self)
        self.url = url
        self.game_id = game_id
        self.game_name = game_name

    def run(self):
        img = self.file_cache(self.url)
        media = Media(table_id=self.game_id, type=0)
        media.cover.save(self.game_name + '.jpg', File(img), save=True)
        print("cover uploaded")
        return "cover uploaded"
