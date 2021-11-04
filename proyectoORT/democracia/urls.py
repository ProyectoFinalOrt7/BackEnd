from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/details/', views.user_detail, name='user_detail'),
    path('user/register/', views.register, name='register'),
    path('ideas/top/', views.top_ideas, name='top_ideas'),
    path('ideas/search/', views.search_ideas,name='search_ideas'),
    path('partidos/', views.partidos,name='partidos'),
    path('distritos/', views.distritos,name='distritos'),
    path('categorias/', views.categorias,name='categorias'),
    path('ideas/crear/', views.crear_idea, name='crear_idea'),
    path('ideas/<pk>/', views.delete_idea, name='delete_idea'),
    path('ideas/<pk>/autor/', views.agregar_autor, name='agregar_autor'),
    path('ideas/<pk>/votar/', views.votar, name='votar'),
    path('merge/search/', views.merge_search, name='merge_search'),
    path('ciudadanos/', views.autores, name='autores'),
]