from django.contrib import admin
from .models import CollectorProfile, Favourite


@admin.register(CollectorProfile)
class CollectorProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'linked_artist', 'created_at')
    search_fields = ('name', 'email', 'phone')
    raw_id_fields = ('user', 'linked_artist')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'painting', 'saved_at')
    search_fields = ('user__username', 'user__email', 'painting__title')

