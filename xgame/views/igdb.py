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
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        r = requests.get(self.base_url + '/search', data=data, headers=headers)
        data = r.json()
        if 'published_at' in data:
            data = sorted(data, key=lambda i: i['published_at'])
        res = {'games': data}
        return JsonResponse(res)


class Cache(Vars):
    data = []
    res = {"message": "Cache failed"}
    links = []

    def cache(self, game_id):
        print("Caching...")
        data = f"fields id, player_perspectives.name, alternative_names.name, collection.name, cover.image_id, first_release_date, genres.name, hypes, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, name, platforms.name, popularity, total_rating, total_rating_count, screenshots.image_id, summary, themes.name, videos.video_id; where id = {game_id};"
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        r = requests.get(self.base_url + '/games', data=data, headers=headers)
        self.data = r.json()
        return self.game_cache()

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

        game = Game(id=data['id'], name=data['name'], perspective=perspective, alternative_names=alternative_names,
                    first_release_date=data['first_release_date'] if 'first_release_date' in data else None,
                    hypes=data['hypes'] if 'hypes' in data else 0, popularity=data['popularity'],
                    total_rating=data['total_rating'] if 'total_rating' in data else 0, developer=developers,
                    total_rating_count=data['total_rating_count'] if 'total_rating_count' in data else 0,
                    summary=data['summary'] if 'summary' in data else None, platform=platforms, genre=genres,
                    theme=themes, publisher=publishers, collection=collection)
        game.save()
        my_game = self.string_to_list([game])
        if 'videos' in data:
            my_game[0]['fields']['video'] = []
            for video in data['videos']:
                v = Media(table_id=game.id, media_id=video['video_id'], type=2)
                v.save()
                link = 'https://www.youtube.com/watch?v=' + video['video_id']
                my_game[0]['fields']['video'].append(link)
                # in new thread
                self.links.append(link)
            # video_thread = UploadVideo(self.links)
            # video_thread.start()

        if 'screenshots' in data:
            screenshots = []
            for screen in data['screenshots']:
                url = self.screenshot + screen['image_id'] + '.jpg'
                screenshots.append(url)
            my_game[0]['fields']['screenshots'] = screenshots
            # new thread
            screenshot_thread = UploadScreen(screenshots, game.id, game.name)
            screenshot_thread.start()
        if 'cover' in data:
            url = self.cover + data['cover']['image_id'] + '.jpg'
            my_game[0]['fields']['cover'] = url
            # new thread
            cover_thread = UploadCover(url, game.id, game.name)
            cover_thread.start()
        print("Cached Successfully")
        res = {'game': my_game[0]['fields']}
        return JsonResponse(res)






