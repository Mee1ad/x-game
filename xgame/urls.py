from django.urls import path
from .views import auth, igdb, api
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('refresh_tokens', auth.RefreshTokens.as_view(), name='refresh_tokens'),
    path('version_control', auth.VersionControl.as_view(), name='version_control'),
    # path('test', auth.test.as_view(), name='test'),
    path('login', auth.Login.as_view(), name='login'),
    path('activate', auth.Activate.as_view(), name='activate'),
    path('signup', auth.Signup.as_view(), name='signup'),
    path('main_games', api.MainGames.as_view(), name='main_games'),
    path('game_detail', api.GameDetail.as_view(), name='game_detail'),
    path('add_review', api.AddReview.as_view(), name='add_review'),
    path('seller_detail', api.SellerDetail.as_view(), name='seller_detail'),
    path('search', api.Search.as_view(), name='search'),
    path('find', igdb.Find.as_view(), name='find'),
    path('add_seller', api.AddSell.as_view(), name='add_seller'),
    path('user_games', api.UserGames.as_view(), name='user_games'),
]

required_auth = ['add_review', 'seller_detail', 'find', 'add_seller', 'user_games', 'refresh_tokens']

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
