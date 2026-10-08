"""
URL configuration for artvault_project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

admin.site.site_header = 'ArtVault · Curatorial Registry'
admin.site.site_title  = 'ArtVault Curator Portal'
admin.site.index_title = 'Vault Archive & Collection Management'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.svg', permanent=True)),
    path('favicon.svg', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.svg', permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('paintings.urls')),
    path('artists/', include('artists.urls')),
    path('accounts/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
