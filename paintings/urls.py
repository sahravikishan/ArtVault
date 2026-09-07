from django.urls import path
from . import views

app_name = 'paintings'

urlpatterns = [
    path('', views.home, name='home'),
    path('painting/<int:pk>/', views.painting_detail, name='detail'),
    # Payment flow
    path('painting/<int:pk>/pay/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/success/<int:order_pk>/', views.order_success, name='order_success'),
    path('payment/certificate/<int:order_pk>/', views.certificate_view, name='certificate'),
    # Exhibitions
    path('exhibitions/', views.exhibition_list, name='exhibition_list'),
    path('exhibitions/<slug:slug>/', views.exhibition_detail, name='exhibition_detail'),
    # Curatorial Inquiries & Private Viewings
    path('painting/<int:pk>/inquire/', views.inquire_view, name='inquire'),
]
