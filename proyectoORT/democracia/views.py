from json.decoder import JSONDecodeError
from django.http import HttpResponse
from django.http.response import HttpResponseNotAllowed, JsonResponse
from proyectoORT.firebase import login_required
from .models.auth import Ciudadano
from .models.democracia import Categoria, Encuesta, IdeaMerge, MergeApproval, OpcionEncuesta, Partido, Distrito, Idea, Voto, VotoEncuesta
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
    ciudadano = Ciudadano.objects.get(email=request.user.username)
    ideas = list(Idea.objects.filter(approved=True))
    ideas.sort(key=lambda x: x.total_votos(), reverse=True)
    ideas_top = ideas[:10]
    return JsonResponse([idea.serialize(request=request) for idea in ideas_top if not idea.es_autor(ciudadano)], safe=False)

@csrf_exempt
@login_required()
def search_ideas(request):
    ideas = list(Idea.objects.filter(approved=True))
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
                        categoria = categoria,
                        subtitulo = data.get('subtitulo')
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
    else:
        idea = Idea.objects.get(pk=pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        return JsonResponse(idea.serialize(request=request))


@csrf_exempt
@login_required()
def autores(request):
    ciudadanos = list(Ciudadano.objects.all())
    if request.GET.get("idea_id"):
        idea = Idea.objects.get(pk=int(request.GET.get("idea_id")))
        idea_autores_ids = [ autor.pk for autor in idea.get_autores() ]
        ciudadanos = [ciudadano for ciudadano in ciudadanos if  ciudadano.pk not in idea_autores_ids]

    if request.GET.get("query"):
        ciudadanos = [ciudadano.serialize(compact=True) for ciudadano in ciudadanos if request.GET.get("query").lower() in ciudadano.nombre.lower()]
    else:
        ciudadanos = [ciudadano.serialize(compact=True) for ciudadano in ciudadanos]

    return JsonResponse(ciudadanos, safe=False)


@csrf_exempt
@login_required()
def agregar_autor(request, pk):
    if request.method == 'PUT':
        idea = Idea.objects.get(pk=pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        if idea.es_autor(ciudadano):
            data = json.loads(request.body)
            nuevo_autor = Ciudadano.objects.get(pk=data["id"])
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
        now = datetime.datetime.now()
        data = json.loads(request.body)
        try:
            voto = Voto.objects.get(ciudadano = ciudadano, idea=idea)
            voto.voto = data['voto'][0].upper()
            voto.comentario = data['comentario']
            voto.fecha = now
        except ObjectDoesNotExist:
            voto = Voto(ciudadano = ciudadano, idea = idea, voto = data['voto'][0].upper(), comentario = data['comentario'], fecha = now)
        voto.save()
    elif request.method == 'DELETE':
        try:
            voto_existente = Voto.objects.get(ciudadano = ciudadano, idea=idea)
            voto_existente.delete()
        except ObjectDoesNotExist:
            pass
    return JsonResponse(idea.serialize(request=request))

@csrf_exempt
@login_required()
def votos(request, pk):
    idea = Idea.objects.get(pk=pk)
    votos = list(Voto.objects.filter(idea=idea).all())
    return JsonResponse([voto.serialize() for voto in votos], safe=False)

@csrf_exempt
@login_required()
def merge_search(request):
    ideas = list(Idea.objects.filter(approved=True))
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

@csrf_exempt
@login_required()
def crear_encuesta(request, idea_pk):
    if request.method == 'POST':
        idea = Idea.objects.get(pk=idea_pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        if not idea.es_autor(ciudadano):
            return HttpResponse('Solo un autor puede crear una encuesta en la idea.', status=403)
        data = json.loads(request.body)
        if 'opciones' not in data:
            return HttpResponse('Se debe enviar la lista de opciones en el body', status=400)
        if len(data['opciones']) < 2:
            return HttpResponse('Se deben enviar al menos dos opciones en una encuesta', status=400)
        if 'pregunta' not in data:
            return HttpResponse('Se debe enviar la pregunta en el body', status=400)
        encuesta = Encuesta(pregunta = data['pregunta'], idea = idea, autor = ciudadano)
        encuesta.save()
        for opcion in data['opciones']:
            new_opcion = OpcionEncuesta(opcion = opcion, encuesta = encuesta)
            new_opcion.save()
        return JsonResponse(encuesta.serialize(request=request))

@csrf_exempt
@login_required()
def votar_encuesta(request, idea_pk, encuesta_pk, opcion_pk):
    if request.method == 'PUT':
        encuesta = Encuesta.objects.get(pk=encuesta_pk)
        opcion = OpcionEncuesta.objects.get(pk=opcion_pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        try:
            voto_existente = VotoEncuesta.objects.get(encuesta=encuesta, ciudadano=ciudadano)
            if voto_existente.opcion.pk != opcion_pk:
                voto_existente.delete()
                new_voto = VotoEncuesta(encuesta=encuesta, ciudadano=ciudadano, opcion=opcion)
                new_voto.save()
        except ObjectDoesNotExist:
            new_voto = VotoEncuesta(encuesta=encuesta, ciudadano=ciudadano, opcion=opcion)
            new_voto.save()
        return JsonResponse(encuesta.serialize(request=request))

@csrf_exempt
@login_required()
def eliminar_voto_encuesta(request, idea_pk, encuesta_pk):
    if request.method == 'DELETE':
        encuesta = Encuesta.objects.get(pk=encuesta_pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        try:
            voto_existente = VotoEncuesta.objects.get(encuesta=encuesta, ciudadano=ciudadano)
            voto_existente.delete()
        except ObjectDoesNotExist:
            pass
        return JsonResponse(encuesta.serialize(request=request))


@csrf_exempt
@login_required()
def ver_encuestas(request, idea_pk):
    idea = Idea.objects.get(pk=idea_pk)
    encuestas = list(Encuesta.objects.filter(idea=idea))
    return JsonResponse([encuesta.serialize(request=request) for encuesta in encuestas], safe=False)

@csrf_exempt
@login_required()
def encuesta(request, idea_pk, encuesta_pk):
    idea = Idea.objects.get(pk=idea_pk)
    encuesta = Encuesta.objects.get(idea=idea, pk=encuesta_pk)
    return JsonResponse(encuesta.serialize(request=request))


@csrf_exempt
@login_required()
def merge(request):
    ciudadano = Ciudadano.objects.get(email=request.user.username)
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'idea_a' not in data:
            return HttpResponse('Se debe enviar idea_a en el body', status=400)
        if 'idea_b' not in data:
            return HttpResponse('Se debe enviar idea_b en el body', status=400)
        ideaA = Idea.objects.get(pk=data['idea_a'])
        ideaB = Idea.objects.get(pk=data['idea_b'])
        now = datetime.datetime.now()
        if 'idea_result' in data:
            categorias = Categoria.objects.all()
            categoria = [categoria for categoria in categorias if categoria.nombre.lower() == data['idea_result'].get("categoria").lower()][0]
            new_idea = Idea (   titulo = data['idea_result'].get('titulo'), 
                                fechaPublicacion = datetime.datetime.now(), 
                                contenido = data['idea_result'].get('contenido'),
                                categoria = categoria,
                                approved = False,
                                subtitulo = data['idea_result']['subtitulo']
                        )
            new_idea.save()
            new_idea.agregar_autor(ciudadano)
            new_idea.save()
            new_merge = IdeaMerge(ideaA=ideaA, ideaB=ideaB, fecha=now, result=new_idea)
        else:
            new_merge = IdeaMerge(ideaA=ideaA, ideaB=ideaB, fecha=now)
        new_merge.save()
        new_merge.calculate_autores()
        new_merge.add_approval(ciudadano)
        ideaA.merge_pendiente = True
        ideaA.save()
        ideaB.merge_pendiente = True
        ideaB.save()
        return JsonResponse(new_merge.serialize(request=request))
    else:
        all_merges = IdeaMerge.objects.all()
        authored_merges = [idea_merge for idea_merge in all_merges if ciudadano.pk in [autor.pk for autor in idea_merge.get_autores()] and not idea_merge.already_approved(ciudadano)]
        return JsonResponse([authored_merge.serialize(request=request) for authored_merge in authored_merges], safe=False)

@csrf_exempt
@login_required()
def approve_merge(request, pk):
    if request.method == 'PUT':
        data = json.loads(request.body)
        merge = IdeaMerge.objects.get(pk=pk)
        ciudadano = Ciudadano.objects.get(email=request.user.username)
        if ciudadano.pk not in [autor.pk for autor in merge.get_autores()]:
            return HttpResponse("El ciudadano {} no es autor del merge {}".format(ciudadano, pk), status=401)
        if data['aprobado']:
            merge.add_approval(ciudadano)
            return JsonResponse(merge.serialize(request=request))
        else:
            merge.ideaA.merge_pendiente = False
            merge.ideaA.save()
            merge.ideaB.merge_pendiente = False
            merge.ideaB.save()
            serialized_merge = merge.serialize(request=request)
            merge.delete()
            return JsonResponse(serialized_merge)
    

