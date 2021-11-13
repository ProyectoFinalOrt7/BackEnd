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
    path('ideas/<pk>/votos/', views.votos, name='votos'),
    path('ideas/<pk>/autor/', views.agregar_autor, name='agregar_autor'),
    path('ideas/<pk>/votar/', views.votar, name='votar'),
    path('merge/search/', views.merge_search, name='merge_search'),
    path('ciudadanos/', views.autores, name='autores'),
    path('ideas/<idea_pk>/crear_encuesta/', views.crear_encuesta, name='crear_encuesta'),
    path('ideas/<idea_pk>/encuestas/<encuesta_pk>/votar/<opcion_pk>/', views.votar_encuesta, name='votar_encuesta'),
    path('ideas/<idea_pk>/encuestas/<encuesta_pk>/votar/', views.eliminar_voto_encuesta, name='eliminar_voto_encuesta'),
    path('ideas/<idea_pk>/encuestas/', views.ver_encuestas, name='ver_encuestas'),
    path('ideas/<idea_pk>/encuestas/<encuesta_pk>/', views.encuesta, name='encuesta'),
    path('merge/', views.merge, name='merge'),
    path('merge/<pk>/approve/', views.approve_merge, name='approve_merge'),
]