from django.urls import path
from . import views

app_name = 'paintings'

urlpatterns = [
    path('', views.home, name='home'),
    path('painting/<int:pk>/', views.painting_detail, name='detail'),
]
