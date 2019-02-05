from django.http import JsonResponse, HttpResponse
from xgame.decorators import try_except
from django.core.files import File
from django.db.models import Q
from xgame.models import *
from .Consts import Vars
import requests
from django.views import View


class Find(Vars):
    @try_except
    def post(self, request):
        game_name = request.GET.get('gameName', '')
        return self.find_game(game_name)
        # game_exists = Game.objects.filter(
        #     Q(name__icontains=game_name) | Q(alternative_names__icontains=game_name)).exists()
        # if game_exists:
        #     games = Game.objects.filter(
        #     Q(name__icontains=game_name) | Q(alternative_names__icontains=game_name))
        #     games_data = []
        #     for game in games:
        #         g = {}
        #         g['id'] = game.id
        #         g['name'] = game.name
        #         cover = Media.objects.get(type=0, table_id=game.id)
        #         g['cover'] = self.cover + cover.media_id + '.jpg'
        #         games_data.append(g)
        #     return JsonResponse({'data': games_data})
        # self.find_game(game_name)

    def find_game(self, game_name):
        data = f'fields name, game; search "{game_name}"; where game != null;'
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        try:
            r = requests.get(self.base_url + '/search', data=data, headers=headers)
            data = r.json()
            print(data)
            res = {'games': data}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class Aparat(View):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
               'Content-Type': 'application/json;charset=UTF-8', 'host': 'api.aparat.com'}
    user = "sjdfnskjfkskf"
    password = "19951374"

    def get(self, request):
        url = 'https://api.aparat.com/fa/v1/user/account/signin/'
        self.headers['Referer'] = 'https://www.aparat.com/authentication'
        self.headers['Access-Control-Request-Method'] = 'POST'
        self.headers['Access-Control-Request-Headers'] = 'content-type,x-sabaenv'
        print(self.headers)
        data = {"account": self.user}
        r = requests.options(url, data=data, headers=self.headers)
        print(r.status_code)
        self.headers['X-SabaENV'] = "{}"
        r = requests.post(url, data=data, headers=self.headers)
        if r.status_code == 200:
            temp_id = r.json()['data']['attributes']['tempId']
            print('tempId:', temp_id)
            self.signin_password(temp_id)
        else:
            print("signin error")
            print(r.status_code)
            print(r.json())
            return HttpResponse("signin error")

    def signin_password(self, temp_id):
        url = 'https://api.aparat.com/fa/v1/user/account/signin_password'
        self.headers['Referer'] = 'https://www.aparat.com/authentication/signin/password'
        self.headers['X-SabaENV'] = '{}'
        data = {"account": self.user, "password": self.password, "tempId": temp_id}
        r = requests.post(url, data=data, headers=self.headers)
        if r.status_code == 200:
            token = r.json()['data']['attributes']['token']
            self.upload_form(token)
        else:
            print("signin_password error")
            return HttpResponse("signin_password error")

    def upload_form(self, token):
        url = 'https://api.aparat.com/fa/v1/video/upload/url/'
        self.headers['Referer'] = 'https://www.aparat.com/uploadnew'
        self.headers['Access-Control-Request-Headers'] = 'Access-Control-Request-Headers'
        self.headers['Access-Control-Request-Method'] = 'POST'
        self.headers['Authorization'] = f'Bearer {token}'
        data = {"url": "https://www.youtube.com/watch?v=eaW0tYpxyp0"}
        r = requests.post(url, data=data, headers=self.headers)
        if r.status_code == 200:
            res = r.json()
            res = res['data']['attributes']
            video_id = res['id']
            upload_id = res['uploadId']
            title = res['title']
            tags = res['tags']
            youtube_url = res['url']
            self.upload(upload_id, video_id, tags, title, youtube_url)
        else:
            print("upload_form error")
            return HttpResponse("upload_form error")

    def upload(self, upload_id, video_id, tags, title, youtube_url):
        url = f'https://api.aparat.com/fa/v1/video/upload/upload/uploadId/{upload_id}'
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
            "tags": tags,
            "title": title,
            "uploadId": upload_id,
            "url": youtube_url,
            "video_pass": "",
            "watermark": "false"
        }
        r = requests.post(url=url, data=data, headers=self.headers)
        if r.status_code == 200:
            link = 'https://aparat.com/v/' + r.json()['data']['attributes']['uid']
            print("Uploaded Successfully")
            print(link)
        else:
            print("upload_form error")
            return HttpResponse("upload_form error")
        

class Cache(Vars, Aparat):
    data = []
    res = {"message": "Cache failed"}

    def cache(self, game_id):
        print("Caching...")
        data = f"fields id, player_perspectives.name, alternative_names.name, collection.name, cover.image_id, first_release_date, genres.name, hypes, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, name, platforms.name, popularity, total_rating, total_rating_count, screenshots.image_id, summary, themes.name, videos.video_id; where id = {game_id};"
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        r = requests.get(self.base_url + '/games', data=data, headers=headers)
        self.data = r.json()
        self.game_cache()
        return JsonResponse(self.res)

    def game_cache(self):
        data = self.data[0]
        game_exists = Game.objects.filter(id=data['id']).exists()
        if game_exists:
            self.res = {"message": "Game Exists"}
            return self.res
        collection = None
        perspective = None
        if 'player_perspectives' in data:
            perspective = data['player_perspectives'][0]['name']
        if 'collection' in data:
            if type(data['collection']) is dict:
                collection = data['collection']['name']
        alternative_names = []
        if 'alternative_names' in data:
            for names in data['alternative_names']:
                alternative_names.append(names['name'])
        platforms = []
        for platform in data['platforms']:
            platforms.append(platform['name'])
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append(genre['name'])
        themes = []
        if 'themes' in data:
            for theme in data['themes']:
                themes.append(theme['name'])
        publishers = []
        for publisher in data['involved_companies']:
            if publisher['publisher']:
                publishers.append(publisher['company']['name'].replace(",", "."))
        developers = []
        for developer in data['involved_companies']:
            if developer['developer']:
                developers.append(developer['company']['name'].replace(",", "."))

        game = Game(id=data['id'], name=data['name'], perspective=perspective, alternative_names=alternative_names,
                    first_release_date=data['first_release_date'] if 'first_release_date' in data else None,
                    hypes=data['hypes'] if 'hypes' in data else None, popularity=data['popularity'],
                    total_rating=data['total_rating'] if 'total_rating' in data else None, developer=developers,
                    total_rating_count=data['total_rating_count'] if 'total_rating_count' in data else None,
                    summary=data['summary'], platform=platforms, genre=genres, theme=themes, publisher=publishers,
                    collection=collection)
        game.save()
        if 'videos' in data:
            for video in data['videos']:
                v = Media(table_id=game.id, media_id=video['video_id'], type=2)
                v.save()
        if 'screenshots' in data:
            for screen in data['screenshots']:
                url = self.screenshot + screen['image_id'] + '.jpg'
                img = self.file_cache(url)
                media = Media(table_id=game.id, type=1)
                media.screenshot.save(data['name'] + '.jpg', File(img), save=True)
        if 'cover' in data:
            url = self.cover + data['cover']['image_id'] + '.jpg'
            img = self.file_cache(url)
            media = Media(table_id=game.id, type=0)
            media.cover.save(data['name'] + '.jpg', File(img), save=True)
        self.res = {"message": "Cached successfully", "id": game.id}
        print("Uploading trailers...")
        # self.signin()
        print("Cached Successfully")
        res = {'message': "Cached Successfully"}
        return JsonResponse(res)






