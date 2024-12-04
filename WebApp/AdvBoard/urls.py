from django.urls import path
from . import views

app_name = 'AdvBoard'

urlpatterns = [
    path('', views.advertisement_list, name='adv_list'),
    path('advertisement/<int:pk>/', views.advertisement_detail, name='adv_detail'),
    path('add/', views.add_advertisement, name='add_adv'),
    path('edit/<int:pk>/', views.edit_advertisement, name='edit_adv'),
    path('delete/<int:pk>/',  views.delete_advertisement, name='delete_adv'),
    path('complete/<int:pk>/',  views.complete_advertisement, name='complete_adv'),
    path('my_ads/', views.my_advertisements, name='my_ads'),
]
