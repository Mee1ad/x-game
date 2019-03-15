from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import escape
from .models import *
from django.utils.safestring import mark_safe


class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'collection', 'first_release_date', 'platform')
    list_filter = ('name', 'collection', 'first_release_date', 'platform')
    search_fields = ['name', 'platform', 'collection']


class SellerAdmin(admin.ModelAdmin):
    list_display = ('link_to_game', 'link_to_user', 'new', 'platform', 'price', 'trends', 'active', 'details')
    list_filter = ('game_id', 'new', 'platform', 'price', 'trends', 'active')
    search_fields = ['game__name']
    readonly_fields = ["image"]

    def image(self, obj):
        image_exists = Media.objects.filter(table_id=obj.pk, type=3).exists()
        if image_exists:
            image = Media.objects.filter(table_id=obj.pk, type=3)
            div = '<div> '
            for img in image:
                i = f'<img src="{img.seller_photos.url}" width="auto" height="200" />'
                div += i
            div += '</div>'
            return mark_safe(div)
        else:
            print('nashode')

    def details(self, obj):
        link = reverse("admin:xgame_seller_change", args=[obj.id])
        return mark_safe(f'<a href="{link}">Show</a>')

    def link_to_game(self, obj):
        link = reverse("admin:xgame_game_change", args=[obj.game.id])
        return mark_safe(f'<a href="{link}">{escape(obj.game.__str__())}</a>')

    def link_to_user(self, obj):
        link = reverse("admin:xgame_user_change", args=[obj.user.id])
        return mark_safe(f'<a href="{link}">{escape(obj.user.__str__())}</a>')

    link_to_game.short_description = 'Game'
    link_to_game.admin_order_field = 'Game'  # Make row sortable
    link_to_user.short_description = 'User'
    link_to_user.admin_order_field = 'User'  # Make row sortable


admin.site.register(User, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Seller, SellerAdmin)

admin.site.site_header = "X-Game"
admin.site.site_title = "X-Game"
