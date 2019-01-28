from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from xgame.models import *
from .igdb import Cache
from .Consts import Vars
import requests


class GameTile(Vars):
    def games(self, request, all_games):
        games = []
        for game in all_games:
            g = game['fields']
            my_game = {'id': game['pk'], 'name': g['name'], 'platform': g['platform']}
            seller_exists = Seller.objects.filter(game=game['pk']).exists()
            my_game['available'] = False
            cover = Media.objects.get(type=0, table_id=game['pk'])
            my_game['cover'] = self.cover + cover.media_id + '.jpg'
            if seller_exists:
                sellers = Seller.objects.filter(game=game['pk'])
                sellers = self.string_to_list(sellers)
                prices = []
                for seller in sellers:
                    s = seller['fields']
                    prices.append(s['price'])
                my_game['low_price'] = min(prices)
                my_game['top_price'] = max(prices)
                my_game['available'] = True
                new_exists = Seller.objects.filter(new=True).exists()
                my_game['new'] = False
                if new_exists:
                    my_game['new'] = True
            games.append(my_game)
        return games


class MainGames(GameTile):
    def get(self, request):
        try:
            all_games = Game.objects.all()
            all_games = self.string_to_list(all_games)
            games = self.games(self, all_games)
            res = {'games': games}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class GameDetail(Cache):
    def get(self, request):
        game_id = request.GET.get('id', '')
        game_exists = Game.objects.filter(pk=game_id).exists()
        if not game_exists:
            self.cache(id)
        game = self.get_game(game_id)
        sellers_detail = self.get_sellers(game_id)
        comments = self.get_reviews(game_id)
        res = {'game': game[0]['fields'], 'sellers': sellers_detail, 'reviews': comments}
        return JsonResponse(res)

    def get_game(self, game_id):
        game = Game.objects.get(pk=game_id)
        game = self.string_to_list([game])
        all_media = Media.objects.filter(table_id=game[0]['pk'], type=1)
        all_media = self.string_to_list(all_media)
        screens = []
        for m in all_media:
            screens.append(self.screenshot + m['fields']['media_id'] + '.jpg')
        game[0]['fields']['screenshots'] = screens
        return game

    def get_sellers(self, game_id):
        all_sellers = Seller.objects.filter(game_id=game_id)
        all_sellers = self.string_to_list(all_sellers)
        sellers_detail = []
        for seller in all_sellers:
            s = seller['fields']
            user = User.objects.get(pk=s['user'])
            seller_detail = {'id': seller['pk'], 'name': f'{user.first_name} {user.last_name}', 'price': s['price'], 'platform': s['platform'],
                             'new': s['new'], 'city': s['city']}
            sellers_detail.append(seller_detail)
        return sellers_detail

    def get_reviews(self, game_id):
        all_comments = Comment.objects.filter(game_id=game_id)
        all_comments = self.string_to_list(all_comments)
        comments = []
        for comment in all_comments:
            c = comment['fields']
            user = User.objects.get(pk=c['user'])
            c['username'] = f'{user.first_name} {user.last_name}'
            # c['time'] = c['created_at'].timestamp()
            comments.append(c)
        return comments


class SellerDetail(Vars):
    def get(self, request):
        data = json.loads(request.body)
        sell_id = data['id']
        seller = get_object_or_404(Seller, pk=sell_id)
        seller = self.string_to_list([seller])
        del seller[0]['fields']['location'], seller[0]['fields']['trends']
        all_media = Media.objects.filter(type=3, table_id=sell_id)
        all_media = self.string_to_list(all_media)
        media = []
        for medi in all_media:
            media.append(self.screenshot + medi['fields']['media_id'] + '.jpg')

        res = {'seller': seller[0]['fields'], 'media': media}
        return JsonResponse(res)


class Search(GameTile):
    def post(self, request):
        data = json.loads(request.body)
        game_name = data['gameName']
        games = Game.objects.filter(name__icontains=f'{game_name}')
        # s = serializers.serialize("json", games)
        games = self.string_to_list(games)
        games = self.games(self, games)
        res = {'games': games}
        return JsonResponse(res)


class SellGame(View):
    def post(self, request):
        data = json.loads(request.body)
        sell = Seller(user_id=request.user.id, game_id=data['game_id'], platform=data['platform'],
                      description=data['description'], location=data['location'],
                      address=data['address'], city=data['city'], new=data['new'], price=data['price'])
        sell.save()


class Review(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            comment = Comment(text=data['text'], rate=data['rate'], game_id=data['gameId'], user_id=request.user.id)
            comment.save()
            res = {'message': "Comment Successfully Added"}
            return JsonResponse(res, status=201)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class GetCountries(Vars):
    def get(self, request):
        try:
            r = requests.get(self.battuta + '/country/all/?key=' + self.battuta_key)
            data = {'countries': r.json()}
            return JsonResponse(data)
        except Exception:
            return JsonResponse(self.get_error())
