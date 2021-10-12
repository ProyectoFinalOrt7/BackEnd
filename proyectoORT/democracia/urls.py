from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/details/', views.user_detail, name='user_detail'),
]