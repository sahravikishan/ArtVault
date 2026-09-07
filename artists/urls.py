from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    # Public views
    path('', views.artist_list, name='list'),
    path('<int:pk>/', views.artist_detail, name='detail'),

    # Artist Studio (Seller / Creator Portal)
    path('dashboard/', views.artist_dashboard, name='dashboard'),
    path('paintings/add/', views.artist_painting_create, name='painting_create'),
    path('paintings/<int:pk>/edit/', views.artist_painting_edit, name='painting_edit'),
    path('paintings/<int:pk>/delete/', views.artist_painting_delete, name='painting_delete'),
    path('profile/edit/', views.artist_profile_edit, name='profile_edit'),
]
