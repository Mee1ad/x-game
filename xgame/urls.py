from django.views.decorators.http import require_POST, require_safe
from django.urls import path
from .views import auth, igdb, api
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('version_control', auth.VersionControl.as_view(), name='version_control'),
    path('login', auth.Login.as_view(), name='login'),
    path('activate', auth.Activate.as_view(), name='activate'),
    path('signup', auth.Signup.as_view(), name='signup'),
    path('main_games', api.MainGames.as_view(), name='main_games'),
    path('game_detail', api.GameDetail.as_view(), name='game_detail'),
    path('review', api.Review.as_view(), name='review'),
    path('seller_detail', api.SellerDetail.as_view(), name='seller_detail'),
    path('search', api.Search.as_view(), name='search'),
    path('find', igdb.Find.as_view(), name='find'),
    path('seller_upload', require_POST(api.SellerPhotosUpload.as_view()), name='seller_upload'),
    # path('image_upload', require_POST(api.ImageUpload.as_view()), name='image_upload'),
    path('get_countries', api.GetCountries.as_view(), name='get_countries'),
    path('get_regions', api.GetRegions.as_view(), name='get_regions'),
    path('get_cities', api.GetCities.as_view(), name='get_cities'),

    path('test', igdb.Aparat.as_view(), name='test'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
