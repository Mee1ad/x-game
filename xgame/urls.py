from django.views.decorators.http import require_POST, require_safe
from django.urls import path
from .views import auth, igdb

urlpatterns = [
    path('version_control', require_safe(auth.VersionControl.as_view()), name='version_control'),
    path('login', require_POST(auth.Login.as_view()), name='login'),
    path('activate', require_POST(auth.Activate.as_view()), name='activate'),
    path('signup', require_POST(auth.Signup.as_view()), name='signup'),

    path('cache', igdb.Search.as_view(), name='cache'),
]