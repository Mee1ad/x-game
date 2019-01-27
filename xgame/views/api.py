from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from xgame.models import *
from .igdb import Cache
from .Consts import Vars


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
    def post(self, request):
        data = json.loads(request.body)
        game_id = data['id']
        game_exists = Game.objects.filter(pk=game_id).exists()
        if not game_exists:
            self.cache(id)
        return self.get_game(game_id)

    def get_game(self, game_id):
        game = Game.objects.get(pk=game_id)
        game = self.string_to_list(game)
        media = Media.objects.filter(table_id=game[0]['pk'], type=1)
        media = self.string_to_list(media)
        screens = []
        for m in media:
            screens.append(self.screenshot + m['fields']['media_id'] + '.jpg')

        game[0]['fields']['screenshots'] = screens
        sellers = Seller.objects.filter(game_id=game_id)
        sellers = self.string_to_list(sellers)
        sellers_detail = []
        for seller in sellers:
            s = seller['fields']
            user = User.objects.get(pk=s['user'])
            seller_detail = {'id': seller['pk'], 'name': user.username, 'price': s['price'], 'platform': s['platform'],
                             'new': s['new']}
            sellers_detail.append(seller_detail)
        res = {'game': game[0]['fields'], 'sellers': sellers_detail}
        return JsonResponse(res)


class SellerDetail(Vars):
    def get(self, request):
        data = json.loads(request.body)
        sell_id = data['id']
        seller = get_object_or_404(Seller, pk=sell_id)
        seller = self.string_to_list(seller)
        del seller[0]['fields']['location'], seller[0]['fields']['trends']
        res = {'seller': seller[0]['fields']}
        return JsonResponse(res)


class Search(GameTile):
    def post(self, request):
        data = json.loads(request.body)
        game_name = data['gameName']
        games = Game.objects.filter(name__icontains=f'{game_name}')
        games = self.string_to_list(games)
        games = self.games(self, games)
        res = {'games': games}
        return JsonResponse(res)


class SellGame(View):
    def post(self, request):
        data = json.loads(request.body)
        sell = Seller(user_id=data['user_id'], game_id=data['game_id'], platform=data['platform'],
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


class GetReviews(Vars):
    def get(self, request):
        try:
            id = request.GET.get('id', '')
            all_comments = Comment.objects.filter(game_id=id)
            all_comments = self.string_to_list(all_comments)
            print(all_comments)
            comments = []
            for comment in all_comments:
                c = comment['fields']
                comments.append(c)
            res = {'comments': comments}
            return JsonResponse(res)
        except Exception as e:
            print(e)
            return HttpResponse(e)

