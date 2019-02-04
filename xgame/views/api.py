from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from xgame.decorators import try_except
from django.views import View
from xgame.models import *
from .Consts import Vars
from .igdb import Cache
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


class GameDetail(Cache):
    @try_except
    def get(self, request):
        game_id = request.GET.get('id', '')
        game_exists = Game.objects.filter(id=game_id).exists()
        if not game_exists:
            self.cache(game_id)
        game = self.get_game(game_id)
        sellers_detail = self.get_sellers(game_id)
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

    def get_sellers(self, game_id):
        all_sellers = Seller.objects.filter(game_id=game_id).exists()
        if all_sellers:
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
        else:
            return None

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
        del seller[0]['fields']['location'], seller[0]['fields']['trends']
        all_media = Media.objects.filter(type=3, table_id=sell_id)
        all_media = self.string_to_list(all_media)
        media = []
        for medi in all_media:
            media.append(self.screenshot + medi['fields']['media_id'] + '.jpg')

        seller[0]['fields']['media'] = media
        res = {'seller': seller[0]['fields']}
        return JsonResponse(res)


class Search(GameTile):
    @try_except
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
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        sell = Seller(user_id=request.user.id, game_id=data['game_id'], platform=data['platform'],
                      description=data['description'], location=data['location'],
                      address=data['address'], city=data['city'], new=data['new'], price=data['price'])
        sell.save()


class Review(View):
    @try_except
    def post(self, request):
        data = json.loads(request.body)
        comment = Comment(text=data['text'], rate=data['rate'], game_id=data['gameId'], user_id=request.user.id)
        comment.save()
        res = {'message': "Comment Successfully Added"}
        return JsonResponse(res, status=201)


class GetCountries(Vars):
    @try_except
    def get(self, request):
        r = requests.get(self.battuta + '/country/all/?key=' + self.battuta_key)
        data = {'countries': r.json()}
        return JsonResponse(data)


class GetRegions(Vars):
    @try_except
    def get(self, request):
        country_code = request.GET.get('countryCode', '')
        r = requests.get(self.battuta + f'/region/{country_code}/all/?key=' + self.battuta_key)
        data = {'regions': r.json()}
        return JsonResponse(data)


class GetCities(Vars):
    @try_except
    def get(self, request):
        country_code = request.GET.get('countryCode', '')
        region_code = request.GET.get('regionCode', '')
        r = requests.get(self.battuta + f'/city/{country_code}/search/?region={region_code}&key='
                         + self.battuta_key)
        print(r)
        data = {'cities': r.json()}
        return JsonResponse(data)


class SellerPhotosUpload(Vars):
    @try_except
    def post(self, request):
        for id, image in zip(request.POST.getlist('id'), request.FILES.getlist('file')):
            media = Media.objects.get(pk=id)
            media.table_id = request.POST.get('id')
            media.seller_photos = image
            media.save()
        return HttpResponse("ok")


class VideoUpload(Vars):
    @try_except
    def post(self, request):
        file = request.FILES['myfile']
        media = Media.objects.get(pk=149)
        media.image = file
        media.save()
        # fs = FileSystemStorage()
        # fs.save(file.name, file)
        # print(filename)
        # uploaded_file_url = fs.url(filename)
        # print(uploaded_file_url)
        return HttpResponse("ok")

