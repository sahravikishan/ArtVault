from django.contrib import admin
from .models import Painting


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year_created', 'style', 'estimated_value')
    search_fields = ('title', 'artist__name', 'story', 'materials')
    list_filter = ('style', 'year_created', 'artist')
    raw_id_fields = ('artist',)
