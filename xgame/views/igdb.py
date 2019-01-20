import requests
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from xgame.models import *
from django.views import View
from .Consts import Vars


class Find(View, Vars):
    def post(self, request):
        data = json.loads(request.body)
        game_name = data['gameName']
        game_exists = Game.objects.filter(
            Q(name__icontains=game_name) | Q(alternative_names__icontains=game_name)).exists()
        if game_exists:
            games = Game.objects.filter(
            Q(name__icontains=game_name) | Q(alternative_names__icontains=game_name))
            games_data = []
            for game in games:
                g = {}
                g['id'] = game.id
                g['name'] = game.name
                cover = Media.objects.get(type=0, table_id=game.id)
                g['cover'] = self.cover + cover.media_id + '.jpg'
                games_data.append(g)
            return JsonResponse({'data': games_data})
        self.find_game(game_name)

    def find_game(self, game_name):
        data = f'fields name; search {game_name}; where game != null;'
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        try:
            r = requests.get(self.base_url + '/search', data=data, headers=headers)
            data = r.json()
            return JsonResponse(data)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class Cache(View, Vars):
    data = []
    res = {"message": "Cache failed"}

    def cache(self, game_id):
        data = f'fields id, alternative_names.name, collection.name, cover.image_id, first_release_date, genres.name,hypes, involved_companies.company.name, involved_companies.developer, involved_companies.publisher,name, platforms.name, popularity, total_rating, total_rating_count, screenshots.image_id, summary,themes.name, videos.video_id, player_perspectives.name; where id = {game_id};'
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        try:
            r = requests.get(self.base_url + '/games', data=data, headers=headers)
            self.data = r.json()
            self.game_cache()
            return JsonResponse(self.res)
        except Exception as e:
            print(e)
            return HttpResponse(e)

    def game_cache(self):
        data = self.data[0]
        game_exists = Game.objects.filter(igdb_id=data['id']).exists()
        if game_exists:
            self.res = "Game exists"
            return self.res
        collection = None
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
        for genre in data['genres']:
            genres.append(genre['name'])
        themes = []
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

        game = Game(igdb_id=data['id'], name=data['name'], alternative_names=alternative_names, collection=collection,
                    first_release_date=data['first_release_date'] if 'first_release_date' in data else None,
                    hypes=data['hypes'] if 'hypes' in data else None, popularity=data['popularity'],
                    total_rating=data['total_rating'] if 'total_rating' in data else None, developer=developers,
                    total_rating_count=data['total_rating_count'] if 'total_rating_count' in data else None,
                    summary=data['summary'], platform=platforms, genre=genres, theme=themes, publisher=publishers)
        game.save()
        if 'videos' in data:
            for video in data['videos']:
                v = Media(table_id=game.id, media_id=video['video_id'], type=2)
                v.save()
        if 'screenshots' in data:
            for screen in data['screenshots']:
                s = Media(table_id=game.id, media_id=screen['image_id'], type=1)
                s.save()
        for cover in data['cover']:
            c = Media(table_id=game.id, media_id=data['cover']['image_id'], type=0)
            c.save()
        self.res = {"message": "Cached successfully"}
