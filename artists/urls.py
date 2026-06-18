from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    path('<int:pk>/', views.artist_detail, name='detail'),
]
