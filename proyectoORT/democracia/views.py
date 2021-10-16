from django.http import HttpResponse
from django.http.response import JsonResponse
from proyectoORT.firebase import login_required
from .models.auth import Ciudadano
from .models.democracia import Partido, Distrito, Idea
from django.views.decorators.csrf import csrf_exempt
import json

@login_required()
def index(request):
    return HttpResponse("Hello {}".format(request.user.username))

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

