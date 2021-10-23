from json.decoder import JSONDecodeError
from django.http import HttpResponse
from django.http.response import HttpResponseNotAllowed, JsonResponse
from proyectoORT.firebase import login_required
from .models.auth import Ciudadano
from .models.democracia import Partido, Distrito, Idea
from django.views.decorators.csrf import csrf_exempt
import json

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
    return JsonResponse([idea.serialize() for idea in ideas_top], safe=False)

@csrf_exempt
@login_required()
def search_ideas(request):
    ideas_search = []
    busqueda = request.GET.get("filtro").lower()
    ideas = list(Idea.objects.all())
    for idea in ideas:
        if busqueda in idea.titulo.lower():
            ideas_search.append(idea)
    return JsonResponse([idea.serialize() for idea in ideas_search], safe=False)


def partidos(request):
    partidos = Partido.objects.all()
    return JsonResponse([partido.serialize() for partido in partidos], safe=False)


def distritos(request):
    distritos = Distrito.objects.all()
    return JsonResponse([distritos.serialize() for distritos in distritos], safe=False)