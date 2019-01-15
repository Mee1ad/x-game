import requests
import json
from django.http import JsonResponse, HttpResponse
from xgame.models import *
from django.views import View
from .Consts import Vars




class Search(View):

    api_key = '5e69676036907c1ee9c1b528f87ba11e'
    image_url = 'https://images.igdb.com/igdb/image/upload/t_720p/'
    screenshot = 'https://images.igdb.com/igdb/image/upload/t_screenshot_big/'
    base_url = 'https://api-v3.igdb.com'
    data = []
    res = "nothing happened"

    def post(self, request):
        print(Vars.ver)
        d = json.loads(request.body)
        id = d['id']
        self.search(id)
        return HttpResponse(self.res)
        # page = d['page']
        # offset = [1, 50, 100, 150, 200]
        # data = f'fields name; where category = 0 & total_rating > 90; offset {offset[page - 1]}'
        # headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        # r = requests.get(self.base_url + '/search', data=data, headers=headers)
        # if r.status_code == 200:
        #     self.data = r.json()
        #     self.game_cache()
        # else:
        #     return HttpResponse("No Content", status=204)

    def search(self, game_id):
        data = f'fields id, alternative_names.name, collection.name, cover.image_id, first_release_date, genres.name,' \
            f' hypes, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, name,' \
            f' platforms.name, popularity, total_rating, total_rating_count, screenshots.image_id, summary, themes.name,' \
            f' videos.video_id; where id = {game_id};'
        headers = {'user-key': self.api_key, 'Accept': 'application/json'}
        r = requests.get(self.base_url + '/games', data=data, headers=headers)
        self.data = r.json()
        self.game_cache()

    def game_cache(self):
        print('cache')
        data = self.data[0]
        game_exists = Game.objects.filter(igdb_id=data['id']).exists()
        if game_exists:
            self.res = "Game Exists"
            return self.res
        collection = None
        if 'collection' in data:
            collection = data['collection']
            if type(collection) is dict:
                collection = collection['id']
            else:
                collection = None
        game = Game(igdb_id=data['id'], name=data['name'],
                    collection=collection, cover=data['cover']['id'],
                    first_release_date=data['first_release_date'] if 'first_release_date' in data else None,
                    hypes=data['hypes'] if 'hypes' in data else None, popularity=data['popularity'],
                    total_rating=data['total_rating'] if 'total_rating' in data else None,
                    total_rating_count=data['total_rating_count'] if 'total_rating_count' in data else None,
                    summary=data['summary'])
        game.save()
        if collection is not None:
            collection = Collection(igdb_id=collection, name=data['collection']['name'])
            collection.save()
        if 'videos' in data:
            for video in data['videos']:
                v = Videos(igdb_id=video['id'], video_id=video['video_id'], game=game)
                v.save()
        if 'screenshots' in data:
            for screen in data['screenshots']:
                s = ScreenShot(igdb_id=screen['id'], image_id=screen['image_id'], game=game)
                s.save()
        if 'alternative_names' in data:
            for name in data['alternative_names']:
                GameName.objects.get_or_create(igdb_id=name['id'], name=name['name'], collection=collection, game=game)
        for genre in data['genres']:
            genre_exists = Genre.objects.filter(igdb_id=genre['id']).exists()
            if not genre_exists:
                g = Genre(igdb_id=genre['id'], name=genre['name'])
                g.save()
            else:
                g = Genre.objects.get(igdb_id=genre['id'])
            game.genres.add(g)
        for theme in data['themes']:
            theme_exists = Genre.objects.filter(igdb_id=theme['id']).exists()
            if not theme_exists:
                t = Theme(igdb_id=theme['id'], name=theme['name'])
                t.save()
            else:
                t = Theme.objects.get(igdb_id=theme['id'])
            game.theme.add(t)
        for platform in data['platforms']:
            platform_exists = Platform.objects.filter(igdb_id=platform['id']).exists()
            if platform_exists:
                p = Platform.objects.get(igdb_id=platform['id'])
            else:
                p = Platform(igdb_id=platform['id'], name=platform['name'])
                p.save()
            game.platforms.add(p)
        for company in data['involved_companies']:
            c = Company(igdb_id=company['company']['id'], name=company['company']['name'],
                        developer=company['developer'], publisher=company['publisher'])
            c.save()
            game.company.add(c)

        GameName.objects.get_or_create(igdb_id=data['id'], name=data['name'], collection=collection, game=game)
        cover = Cover(igdb_id=data['cover']['id'], image_id=data['cover']['image_id'], game=game)
        cover.save()
        # res = {'message': 'Add To Database Successfully'}
        # return JsonResponse(res)
        self.res = "tamam"
        return self.res
