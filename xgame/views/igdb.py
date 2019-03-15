from django.http import JsonResponse, HttpResponse
from xgame.decorators import try_except
from django.core.files import File
from django.db.models import Q
from xgame.models import *
from .Consts import Vars
import requests
from django.views import View
# from threading import Thread
import threading
from xgame.decorators import try_except
from xgame.threads import UploadVideo, UploadScreen, UploadCover


class Find(Vars):
    @try_except
    def get(self, request):
        game_name = request.GET.get('gameName', '')
        return self.find_game(game_name)

    def find_game(self, game_name):
        data = f'fields name, game, published_at; search "{game_name}"; where game != null;'
        headers = {'user-key': self.api_key, 'Accept': 'application/json', 'user-agent': self.user_agent}
        r = requests.post(self.base_url + '/search', data=data, headers=headers)
        data = r.json()
        # if 'published_at' in data:
        #     data = sorted(data, key=lambda i: i['published_at'])
        res = {'games': data}
        return JsonResponse(res)


class Cache(Vars):
    data = []
    res = {"message": "Cache failed"}
    links = []
    my_game = []
    screenshots = []
    url = ""
    game = None
    video = None
    error = False

    def cache(self, game_id):
        try:
            print("Getting Game Data...")
            data = f"fields id, player_perspectives.name, alternative_names.name, collection.name, cover.image_id, first_release_date, genres.name, hypes, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, name, platforms.name, popularity, total_rating, total_rating_count, screenshots.image_id, summary, themes.name, videos.video_id; where id = {game_id};"
            headers = {'user-key': self.api_key, 'Accept': 'application/json', 'user-agent': self.user_agent}
            r = requests.get(self.base_url + '/games', data=data, headers=headers)
            self.data = r.json()
            if len(r.json()) == 0:
                return
            return self.game_details()
        except Exception:
            self.error = True

    def game_details(self):
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
        if 'platforms' in data:
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
        developers = []
        if 'involved_companies' in data:
            for publisher in data['involved_companies']:
                if publisher['publisher']:
                    publishers.append(publisher['company']['name'].replace(",", "."))
            for developer in data['involved_companies']:
                if developer['developer']:
                    developers.append(developer['company']['name'].replace(",", "."))

        self.game = Game(id=data['id'], name=data['name'], perspective=perspective, alternative_names=alternative_names,
                         first_release_date=data['first_release_date'] if 'first_release_date' in data else None,
                         hypes=data['hypes'] if 'hypes' in data else 0, popularity=data['popularity'],
                         total_rating=data['total_rating'] if 'total_rating' in data else 0, developer=developers,
                         total_rating_count=data['total_rating_count'] if 'total_rating_count' in data else 0,
                         summary=data['summary'] if 'summary' in data else None, platform=platforms, genre=genres,
                         theme=themes, publisher=publishers, collection=collection)

        self.my_game = self.string_to_list([self.game])

        if 'videos' in data:
            self.my_game[0]['video'] = []
            for v in data['videos']:
                self.video = Media(table_id=self.game.id, media_id=v['video_id'], type=2)
                link = 'https://www.youtube.com/watch?v=' + v['video_id']
                self.my_game[0]['video'].append(link)
                self.links.append(link)
        self.screenshots = []
        if 'screenshots' in data:
            for screen in data['screenshots']:
                url = self.screenshot + screen['image_id'] + '.jpg'
                self.screenshots.append(url)
            self.my_game[0]['screenshots'] = self.screenshots
        if 'cover' in data:
            self.url = self.cover + data['cover']['image_id'] + '.jpg'
            self.my_game[0]['cover'] = self.url
            if 'cover' == '':
                self.error = True

    def cache_game(self):
        try:
            print("Caching...")
            self.game.save()
            self.video.save()
            # video_thread = UploadVideo(self.links)
            # video_thread.start()
            screenshot_thread = UploadScreen(self.screenshots, self.game.id, self.game.name)
            screenshot_thread.start()
            cover_thread = UploadCover(self.url, self.game.id, self.game.name)
            cover_thread.start()
            print("Cached Successfully")
            return True
        except Exception:
            return False



    def response(self):
        if len(self.my_game) == 0:
            return JsonResponse({"Message": "Game Not Found"}, status=404)
        res = {'game': self.my_game[0]}
        return JsonResponse(res)






