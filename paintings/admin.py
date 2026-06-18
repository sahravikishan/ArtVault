from django.contrib import admin
from .models import Painting
from .templatetags.currency_tags import inr

@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year_created', 'style', 'formatted_value')
    search_fields = ('title', 'artist__name', 'story', 'materials')
    list_filter = ('style', 'year_created', 'artist')
    raw_id_fields = ('artist',)

    def formatted_value(self, obj):
        return inr(obj.estimated_value)
    formatted_value.short_description = 'Estimated Value'
