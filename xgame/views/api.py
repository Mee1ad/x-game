from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from xgame.decorators import try_except
from django.views import View
from xgame.models import *
from .Consts import Vars, Validation
from .igdb import Cache
from xgame.threads import UploadCover


class GameTile(Vars):
    def games(self, request, all_games):
        games = []
        for game in all_games:
            g = game['fields']
            my_game = {'id': game['pk'], 'name': g['name'], 'platform': g['platform']}
            seller_exists = Seller.objects.filter(game=game['pk']).exists()
            my_game['available'] = False
            cover_exists = Media.objects.filter(type=0, table_id=game['pk']).exists()
            cover = ""
            if cover_exists:
                cover = Media.objects.get(type=0, table_id=game['pk'])
                my_game['cover'] = self.media + cover.cover.url
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
    @try_except
    def get(self, request):
        all_games = Game.objects.all()
        all_games = self.string_to_list(all_games)
        games = self.games(self, all_games)
        res = {'games': games}
        return JsonResponse(res)


class UserGames(GameTile):
    @try_except
    def get(self, request):
        seller_exists = Seller.objects.filter(user_id=request.user.id).exists()
        my_games = []
        if seller_exists:
            sellers = Seller.objects.filter(user_id=request.user.id)
            for seller in sellers:
                seller = self.string_to_list([seller])
                seller = seller[0]['fields']
                game_detail = {}
                game_detail['price'] = seller['price']
                game_detail['date'] = seller['created_at'].split(',')[0]
                game_detail['active'] = seller['active']
                game = Game.objects.get(pk=seller['game'])
                game = self.string_to_list([game])
                game_detail['game_name'] = game[0]['fields']['name']
                game_detail['game_id'] = game[0]['pk']
                cover_exists = Media.objects.filter(type=0, table_id=game[0]['pk']).exists()
                if cover_exists:
                    cover = Media.objects.get(type=0, table_id=game[0]['pk'])
                    game_detail['cover'] = self.media + cover.cover.url
                else:
                    cover_thread = UploadCover(game_detail[url], self.game.id, self.game.name)
                my_games.append(game_detail)
        res = {'games': my_games}
        return JsonResponse(res)


class GameDetail(Cache):
    @try_except
    def get(self, request):
        game_id = request.GET.get('id', '')
        game_exists = Game.objects.filter(id=game_id).exists()
        if not game_exists:
            self.cache(game_id)
            return self.response()
        game = self.get_game(game_id)
        sellers_detail = self.get_sellers_with_game_id(game_id)
        comments = self.get_reviews(game_id)
        res = {'game': game[0]['fields'], 'sellers': sellers_detail, 'reviews': comments}
        return JsonResponse(res)

    def get_game(self, game_id):
        game = Game.objects.get(id=game_id)
        game = self.string_to_list([game])
        all_media = Media.objects.filter(table_id=game[0]['pk'], type=1)
        screens = []
        for media in all_media:
            screens.append(self.media + media.screenshot.url)
        game[0]['fields']['screenshots'] = screens
        cover = Media.objects.get(table_id=game_id, type=0)
        game[0]['fields']['cover'] = self.media + cover.cover.url
        return game

    def get_sellers_with_user_id(self, user_id):
        all_sellers = Seller.objects.filter(user_id=user_id).exists()
        if all_sellers:
            all_sellers = Seller.objects.filter(user_id=user_id)
            return self.get_seller(all_sellers)
        else:
            return None

    def get_sellers_with_game_id(self, game_id):
        all_sellers = Seller.objects.filter(game_id=game_id).exists()
        if all_sellers:
            all_sellers = Seller.objects.filter(game_id=game_id)
            return self.get_seller(all_sellers)
        else:
            return None

    def get_seller(self, all_sellers):
        all_sellers = self.string_to_list(all_sellers)
        sellers_detail = []
        for seller in all_sellers:
            s = seller['fields']
            user = User.objects.get(pk=s['user'])
            seller_detail = {'id': seller['pk'], 'name': f'{user.first_name} {user.last_name}', 'price': s['price'],
                             'platform': s['platform'], 'active': s['active'], 'new': s['new'], 'city': s['city']}
            sellers_detail.append(seller_detail)
        return sellers_detail

    def get_reviews(self, game_id):
        all_comments = Comment.objects.filter(game_id=game_id).exists()
        if all_comments:
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
        else:
            return None


class SellerDetail(Vars):
    @try_except
    def get(self, request):
        sell_id = request.GET.get('id', '')
        seller = get_object_or_404(Seller, pk=sell_id)
        seller = self.string_to_list([seller])
        fields = seller[0]['fields']
        del fields['location'], fields['trends']
        user = User.objects.get(pk=fields['user'])
        fields['user'] = f'{user.first_name} {user.last_name}'
        fields['phone'] = user.phone
        fields['email'] = user.email
        all_media = Media.objects.filter(type=3, table_id=sell_id)
        media = []
        for medi in all_media:
            media.append(self.media + medi.seller_photos.url)

        fields['media'] = media
        res = {'seller': fields}
        return JsonResponse(res)


class AddReview(Vars, Validation):
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        valid = {'text': self.validation('text', data['text']),
                 'rate': self.validation('rate', data['rate']),
                 'gameId': self.validation('id', data['gameId'])}
        for key, value in valid.items():
            if "no match" in value:
                return JsonResponse({'message': f'{key} ' + request.response['invalid']})
        comment = Comment(text=data['text'], rate=data['rate'], game_id=data['gameId'], user_id=request.user.id)
        comment.save()
        res = {'message': request.response['add_review']}
        return JsonResponse(res, status=201)


class AddSell(Cache):
    @try_except
    def post(self, request):
        data = json.loads(request.POST.get('data'))
        game_id = data['game_id']
        game_exists = Game.objects.filter(id=game_id).exists()
        if not game_exists:
            self.cache(game_id)
            self.cache_game()
        sell = Seller(user_id=request.user.id, game_id=game_id, platform=data['platform'],
                      description=data['description'], location=data['location'], address=data['address'],
                      city="", new=data['new'], price=data['price'], phone=data['phone'])
        sell.save()
        for image in request.FILES.getlist('file'):
            if image is not None:
                media = Media(table_id=sell.id, seller_photos=image, type=3)
                media.save()
        res = {"message": request.response['add_sell']}
        return JsonResponse(res)
