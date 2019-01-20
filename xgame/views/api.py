from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from xgame.models import *
from django.views import View
from .igdb import Cache
import ast
from .Consts import Vars


class GameTile(View, Vars):


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
                sellers = serializers.serialize("json", sellers)
                sellers = sellers.replace('false', 'False').replace('true', 'True')
                sellers = ast.literal_eval(sellers)
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
            all_games = serializers.serialize("json", all_games)
            all_games = all_games.replace('false', 'False').replace('true', 'True')
            all_games = ast.literal_eval(all_games)
            games = self.games(self, all_games)
            res = {'games': games}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)


class GameDetail(Cache):
    def post(self, request):
        data = json.loads(request.body)
        game_id = data['id']
        game_exists = Game.objects.filter(pk=game_id).exists()
        if not game_exists:
            self.cache(id)
        return self.get_game(game_id)

    def get_game(self, game_id):
        game = Game.objects.get(pk=game_id)
        game = serializers.serialize("json", [game])
        game = game.replace('false', 'False').replace('true', 'True')
        game = ast.literal_eval(game)
        sellers = Seller.objects.filter(game_id=game_id)
        sellers = serializers.serialize("json", sellers)
        sellers = sellers.replace('false', 'False').replace('true', 'True')
        sellers = ast.literal_eval(sellers)
        sellers_detail = []
        for seller in sellers:
            s = seller['fields']
            user = User.objects.get(pk=s['user'])
            seller_detail = {'id': seller['pk'], 'name': user.username, 'price': s['price'], 'platform': s['platform'],
                             'new': s['new']}
            sellers_detail.append(seller_detail)
        res = {'game': game[0]['fields'], 'sellers': sellers_detail}
        return JsonResponse(res)


class SellerDetail(View, Vars):
    def get(self, request):
        data = json.loads(request.body)
        sell_id = data['id']
        seller = get_object_or_404(Seller, pk=sell_id)
        seller = serializers.serialize("json", [seller])
        seller = seller.replace('false', 'False').replace('true', 'True')
        seller = ast.literal_eval(seller)
        del seller[0]['fields']['location'], seller[0]['fields']['trends']
        res = {'seller': seller[0]['fields']}
        return JsonResponse(res)


class Search(GameTile):
    def post(self, request):
        data = json.loads(request.body)
        game_name = data['gameName']
        games = Game.objects.filter(name__icontains=f'{game_name}')
        games = serializers.serialize("json", games).replace('false', 'False').replace('true', 'True')
        games = ast.literal_eval(games)
        games = self.games(self, games)
        res = {'games': games}
        return JsonResponse(res)


class SellGame(View):
    def post(self, request):
        data = json.loads(request.body)
