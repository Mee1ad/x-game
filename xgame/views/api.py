from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from secrets import token_hex
from xgame.models import *
from django.views import View
import json
import random


class SellGame(View):
    pass
