from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/details/', views.user_detail, name='user_detail'),
    path('user/register/', views.register, name='register'),
    path('ideas/top/', views.top_ideas, name='top_ideas'),
    path('ideas/search/', views.search_ideas,name='search_ideas'),
]