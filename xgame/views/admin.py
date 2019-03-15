from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from xgame.decorators import try_except
from django.views import View
from xgame.models import *
from .Consts import Vars, Validation
from .igdb import Cache
from xgame.threads import UploadCover


class NewSeller(Vars):
    def post(self, request):
        sellers = Seller.objects.filter(active=0)
        sellers = self.string_to_list(sellers)
        return JsonResponse({'sellers': sellers})


class AcceptSeller(Vars):
    def post(self, request):
        data = json.loads(request.body)
        id = data['id']
        seller_exist = Seller.objects.filter(pk=id).exists()
        if seller_exist:
            seller = Seller.objects.get(pk=id)
            seller.active = 0
            seller.save()
        return JsonResponse({'message': 'Accepted'})


