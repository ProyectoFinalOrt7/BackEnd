from json.decoder import JSONDecodeError
from django.http import HttpResponse
from django.http.response import HttpResponseNotAllowed, JsonResponse
from proyectoORT.firebase import login_required
from .models.auth import Ciudadano
from .models.democracia import Categoria, Partido, Distrito, Idea, Voto
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import BadRequest, ObjectDoesNotExist
import json
import datetime

@login_required()
def index(request):
    return HttpResponse("Hello {}".format(request.user.username))

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ciudadano = Ciudadano.register_new(data)
        return JsonResponse(ciudadano.serialize())
    return HttpResponseNotAllowed('Register must be POST')

@csrf_exempt
@login_required()
def user_detail(request):
    ciudadano = Ciudadano.objects.get(email=request.user.username)
    if request.method in ['POST', 'PUT']:
        data = json.loads(request.body)
        ciudadano.nombre = data.get('nombre', ciudadano.nombre)
        ciudadano.dni = data.get('dni', ciudadano.dni)
        if 'partido' in data:
            if data['partido']:
                ciudadano.partido = Partido.objects.get(nombre=data['partido'])
            else:
                ciudadano.partido = None
        if 'distrito' in data:
            if data['distrito']:
                ciudadano.distrito = Distrito.objects.get(nombre=data['distrito'])
            else:
                ciudadano.distrito = None
        ciudadano.save()
    return JsonResponse(ciudadano.serialize())

@csrf_exempt
@login_required()
def top_ideas(request):
    ideas = list(Idea.objects.all())
    ideas.sort(key=lambda x: x.total_votos(), reverse=True)
    ideas_top = ideas[:10]
    return JsonResponse([idea.serialize(request=request) for idea in ideas_top], safe=False)

@csrf_exempt
@login_required()
def search_ideas(request):
    ideas = list(Idea.objects.all())
    if request.GET.get("filtro"):
        ideas = [idea for idea in ideas if request.GET.get("filtro").lower() in idea.titulo.lower()]
    
    if request.GET.get("categoria"):
        ideas = [idea for idea in ideas if idea.categoria.nombre.lower() == request.GET.get("categoria").lower()]

    if request.GET.get("propias") and request.GET.get("propias") == 'true':
        ideas = [idea for idea in ideas if idea.autores.filter(email=request.user.username).exists()]

    return JsonResponse([idea.serialize(request=request) for idea in ideas], safe=False)

@csrf_exempt
@login_required()
def crear_idea(request):
    if request.method in ['POST']:
        data = json.loads(request.body)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        categorias = Categoria.objects.all()
        categoria = [categoria for categoria in categorias if categoria.nombre.lower() == data.get("categoria").lower()][0]
        idea = Idea (   titulo = data.get('titulo'), 
                        fechaPublicacion = datetime.datetime.now(), 
                        contenido = data.get('contenido'),
                        categoria = categoria
                    )
        idea.save()
        idea.agregar_autor(ciudadano)
        idea.save()
        return JsonResponse(idea.serialize(request=request))


@csrf_exempt
@login_required()
def delete_idea(request, pk):
    if request.method == 'DELETE':
        idea = Idea.objects.get(pk=pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        if idea.es_autor(ciudadano):
            idea.delete()
            return HttpResponse('Deleted')
        else:
            return HttpResponse('Solo un autor puede eliminar una idea.', status=403)


@csrf_exempt
@login_required()
def agregar_autor(request, pk):
    if request.method == 'PUT':
        idea = Idea.objects.get(pk=pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        if idea.es_autor(ciudadano):
            data = json.loads(request.body)
            nuevo_autor = Ciudadano.objects.get(pk=data["autor_id"])
            idea.agregar_autor(nuevo_autor)
            idea.save()
            return JsonResponse(idea.serialize(request=request))
        else:
            return HttpResponse('Solo un autor puede agregar otro autor.', status=403)

@csrf_exempt
@login_required()
def votar(request, pk):
    idea = Idea.objects.get(pk=pk)
    ciudadano = Ciudadano.objects.get(email=request.user.username)
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            voto = Voto.objects.get(ciudadano = ciudadano, idea=idea)
            voto.voto = data['voto'][0].upper()
            voto.comentario = data['comentario']
        except ObjectDoesNotExist:
            voto = Voto(ciudadano = ciudadano, idea = idea, voto = data['voto'][0].upper(), comentario = data['comentario'])
        voto.save()
        return JsonResponse(voto.serialize())
    elif request.method == 'DELETE':
        try:
            voto_existente = Voto.objects.get(ciudadano = ciudadano, idea=idea)
            voto_existente.delete()
            return HttpResponse('Deleted')
        except ObjectDoesNotExist:
            return HttpResponse('Idea no votada previamente', status=400)

@csrf_exempt
@login_required()
def merge_search(request):
    ideas = list(Idea.objects.all())
    if request.GET.get("ideaid"):
        idea_search = Idea.objects.get(pk=int(request.GET.get("ideaid")))
        ideas = [idea for idea in ideas if idea.categoria is not None and idea.categoria.nombre == idea_search.categoria.nombre and idea.pk != idea_search.pk]
    return JsonResponse([idea.serialize(request=request) for idea in ideas], safe=False)

def partidos(request):
    partidos = Partido.objects.all()
    return JsonResponse([partido.serialize() for partido in partidos], safe=False)


def distritos(request):
    distritos = Distrito.objects.all()
    return JsonResponse([distrito.serialize() for distrito in distritos], safe=False)

def categorias(request):
    categorias = Categoria.objects.all()
    return JsonResponse([categoria.serialize() for categoria in categorias], safe=False)