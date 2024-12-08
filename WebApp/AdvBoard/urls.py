from django.urls import path
from . import views

app_name = 'AdvBoard'

urlpatterns = [
    path('', views.advertisement_list, name='adv_list'),
    path('advertisement/<int:pk>/', views.advertisement_detail, name='adv_detail'),
    path('add/', views.add_advertisement, name='add_adv'),
    path('edit/<int:pk>/', views.edit_advertisement, name='edit_adv'),
    path('advertisement/<int:pk>/delete/', views.delete_advertisement, name='delete_adv'),
    path('advertisement/<int:pk>/delete_completely/', views.delete_completely, name='delete_completely'),
    path('complete/<int:pk>/',  views.complete_advertisement, name='complete_advertisement'),
    path('my_ads/', views.my_advertisements, name='my_ads'),
    path('<int:pk>/<str:action>/', views.vote, name='toggle_like_dislike'),
    path('advertisement/<int:pk>/activate/', views.activate_advertisement, name='activate_adv'),
    ]
