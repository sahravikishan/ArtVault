from django.contrib import admin
from .models import Artist


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_year')
    search_fields = ('name', 'bio')
    list_filter = ('birth_year',)
