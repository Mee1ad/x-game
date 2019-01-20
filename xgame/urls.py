from django.views.decorators.http import require_POST, require_safe
from django.urls import path
from .views import auth, igdb, api

urlpatterns = [
    path('version_control', require_safe(auth.VersionControl.as_view()), name='version_control'),
    path('login', require_POST(auth.Login.as_view()), name='login'),
    path('activate', require_POST(auth.Activate.as_view()), name='activate'),
    path('signup', require_POST(auth.Signup.as_view()), name='signup'),
    path('main_games', require_safe(api.MainGames.as_view()), name='main_games'),
    path('game_detail', require_POST(api.GameDetail.as_view()), name='game_detail'),
    path('seller_detail', require_safe(api.SellerDetail.as_view()), name='seller_detail'),
    path('search', require_POST(api.Search.as_view()), name='search'),
    path('find', require_POST(igdb.Find.as_view()), name='find'),

]