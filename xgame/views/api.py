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
            my_game = {'id': game['id'], 'name': game['name'], 'platform': game['platform']}
            seller_exists = Seller.objects.filter(game=game['id'], active=True).exists()
            my_game['available'] = False
            cover_exists = Media.objects.filter(type=0, table_id=game['id']).exists()
            cover = ""
            if cover_exists:
                cover = Media.objects.get(type=0, table_id=game['id'])
                my_game['cover'] = self.media + cover.cover.url
            if seller_exists:
                sellers = Seller.objects.filter(game=game['id'], active=True)
                sellers = self.string_to_list(sellers)
                prices = []
                for seller in sellers:
                    prices.append(seller['price'])
                    my_game['new'] = seller['new']
                my_game['low_price'] = min(prices)
                my_game['top_price'] = max(prices)
                my_game['available'] = True
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
                seller = self.string_to_list([seller])[0]
                game_detail = {}
                game_detail['price'] = seller['price']
                game_detail['date'] = seller['created_at'].split(',')[0]
                game_detail['active'] = seller['active']
                game = Game.objects.get(pk=seller['game'])
                game = self.string_to_list([game])
                game_detail['game_name'] = game[0]['name']
                game_detail['game_id'] = game[0]['id']
                cover_exists = Media.objects.filter(type=0, table_id=game[0]['id']).exists()
                if cover_exists:
                    cover = Media.objects.get(type=0, table_id=game[0]['id'])
                    game_detail['cover'] = self.media + cover.cover.url
                else:
                    cover_thread = UploadCover(game_detail['url'], self.game.id, self.game.name)
                my_games.append(game_detail)
        res = {'games': my_games}
        return JsonResponse(res)


class GameDetail(Cache):
    @try_except
    def get(self, request):
        if self.error is True:
            return JsonResponse({'message': request.response['bad_game']}, status=400)
        game_id = request.GET.get('id', '')
        location = request.GET.get('location', '')
        game_exists = Game.objects.filter(id=game_id).exists()
        if not game_exists:
            self.cache(game_id)
            return self.response()
        game = self.get_game(game_id)
        sellers_detail = self.get_sellers_with_game_id(game_id)
        comments = self.get_reviews(game_id)
        res = {'game': game[0], 'sellers': sellers_detail, 'reviews': comments}
        return JsonResponse(res)

    def get_game(self, game_id):
        game = Game.objects.get(id=game_id)
        game = self.string_to_list([game])
        all_media = Media.objects.filter(table_id=game[0]['id'], type=1)
        screens = []
        for media in all_media:
            screens.append(self.media + media.screenshot.url)
        game[0]['screenshots'] = screens
        cover = Media.objects.get(table_id=game_id, type=0)
        game[0]['cover'] = self.media + cover.cover.url
        return game

    def get_sellers_with_user_id(self, user_id):
        all_sellers = Seller.objects.filter(user_id=user_id).exists()
        if all_sellers:
            all_sellers = Seller.objects.filter(user_id=user_id)
            return self.get_seller(all_sellers)
        else:
            return None

    def get_sellers_with_game_id(self, game_id):
        all_sellers = Seller.objects.filter(game_id=game_id, active=True).exists()
        if all_sellers:
            all_sellers = Seller.objects.filter(game_id=game_id, active=True)
            return self.get_seller(all_sellers)
        else:
            return None

    def get_seller(self, all_sellers):
        all_sellers = self.string_to_list(all_sellers)
        sellers_detail = []
        for seller in all_sellers:
            user = User.objects.get(pk=seller['user'])
            seller_detail = {'id': seller['id'], 'name': f'{user.first_name} {user.last_name}', 'price': seller['price'],
                             'platform': seller['platform'], 'active': seller['active'], 'new': seller['new']}
            sellers_detail.append(seller_detail)
        return sellers_detail

    def get_reviews(self, game_id):
        all_comments = Comment.objects.filter(game_id=game_id).exists()
        if all_comments:
            all_comments = Comment.objects.filter(game_id=game_id)
            all_comments = self.string_to_list(all_comments)
            comments = []
            for comment in all_comments:
                user = User.objects.get(pk=comment['user'])
                comment['username'] = f'{user.first_name} {user.last_name}'
                # c['time'] = c['created_at'].timestamp()
                comments.append(comment)
            return comments
        else:
            return None


class SellerDetail(Vars):
    @try_except
    def get(self, request):
        sell_id = request.GET.get('id', '')
        seller = get_object_or_404(Seller, pk=sell_id)
        seller = self.string_to_list([seller])
        fields = seller[0]
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
                 'game_id': self.validation('id', data['game_id'])}
        for key, value in valid.items():
            if "no match" in value:
                return JsonResponse({'message': f'{key} ' + request.response['invalid']}, status=406)
        comment = Comment(text=data['text'], rate=data['rate'], game_id=data['game_id'], user_id=request.user.id)
        comment.save()
        res = {'message': request.response['add_review']}
        return JsonResponse(res, status=201)


class AddSell(Cache):
    @try_except
    def post(self, request):
        data = json.loads(request.POST.get('data'))
        game_id = data['game_id']
        if self.error is False:
            return JsonResponse({'message': request.response['bad_game']}, status=400)
        game_exists = Game.objects.filter(id=game_id).exists()
        if not game_exists:
            self.cache(game_id)
            if self.game is None:
                res = {"message": 'game id is wrong'}
                return JsonResponse(res, 400)
            self.cache_game()
        sell = Seller(user_id=request.user.id, game_id=game_id, platform=data['platform'],
                      description=data['description'], location=data['location'], address=data['address'],
                      new=data['new'], price=data['price'], phone=data['phone'])
        sell.save()
        for image in request.FILES.getlist('file'):
            if image is not None:
                media = Media(table_id=sell.id, seller_photos=image, type=3)
                media.save()
        staff = self.get_staff()
        game = Game.objects.get(pk=game_id).name
        staff.send_message(title="New Game For Sale", body=game, sound="mysound")
        res = {"message": request.response['add_sell']}
        return JsonResponse(res)
