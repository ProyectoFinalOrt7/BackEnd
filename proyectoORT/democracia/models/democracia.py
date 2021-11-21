from django.db import models
from .auth import Ciudadano

class Partido(models.Model):
    nombre = models.CharField(max_length=128)

    def serialize(self):
        return {
            'id': self.pk,
            'nombre': self.nombre
        }
    
    def __str__(self):
        return self.nombre

class Distrito(models.Model):
    nombre = models.CharField(max_length=128)

    def serialize(self):
        return {
            'id': self.pk,
            'nombre': self.nombre
        }
    
    def __str__(self):
        return self.nombre

class Voto(models.Model):
    ciudadano = models.ForeignKey('Ciudadano', on_delete=models.CASCADE)
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)
    voto = models.CharField(max_length=1, choices=[('A', 'Afirmativo'), ('N', 'Negativo')])
    comentario = models.CharField(max_length=1024, default='')
    fecha = models.DateTimeField(null=True, blank=True)

    def serialize(self):
        return {
            'id': self.pk,
            'ciudadano': self.ciudadano.serialize(compact=True),
            'voto': 'Afirmativo' if self.voto == 'A' else 'Negativo',
            'comentario': self.comentario,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M') if self.fecha else None
        }

    def __str__(self):
        return '{} [{}] {}'.format(self.idea.titulo, self.ciudadano.nombre, 'Afirmativo' if self.voto == 'A' else 'Negativo')

class Idea(models.Model):
    titulo = models.CharField(max_length=128)
    fechaPublicacion = models.DateTimeField()
    contenido = models.TextField(max_length=1024)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, default=None, blank=True)
    autores = models.ManyToManyField('Ciudadano')
    approved = models.BooleanField(default=True)
    merge_pendiente = models.BooleanField(default=False)
    
    def votos_positivos(self):
        return Voto.objects.filter(idea=self, voto='A').count()

    def votos_negativos(self):
        return Voto.objects.filter(idea=self, voto='N').count()

    def total_votos(self):
        return self.votos_positivos() - self.votos_negativos()

    def serialize(self, request=None, votos=False):
        if request: 
            ciudadano = Ciudadano.objects.get(email=request.user.username)
            es_autor = self.es_autor(ciudadano)
            voto_a_favor = self.voto_a_favor(ciudadano)
            voto_en_contra = self.voto_en_contra(ciudadano)
        else:
            es_autor = None
            voto_a_favor = None
            voto_en_contra = None
        serialized = {
            'id': self.pk,
            'titulo': self.titulo,
            'fechaPublicacion': self.fechaPublicacion.strftime('%Y-%m-%d %H:%M'),
            'contenido': self.contenido,
            'votosPositivos': self.votos_positivos(),
            'votosNegativos': self.votos_negativos(),
            'votosTotales': self.votos_positivos() - self.votos_negativos(),
            'categoria': self.categoria.nombre if self.categoria else None,
            'autores': self.get_autores(serialized=True),
            'es_autor': es_autor,
            'voto_a_favor': voto_a_favor,
            'voto_en_contra': voto_en_contra,
            'aprobada': self.approved,
            'merge_pendiente': self.merge_pendiente
        }
        if votos:
            serialized["votos"] = [voto.serialize() for voto in votos]
        return serialized
    
    def __str__(self):
        return "[{}] {} {}/{}".format(self.fechaPublicacion.strftime('%Y-%m-%d %H:%M'), self.titulo, self.votos_positivos(), self.votos_negativos())

    def get_autores(self, serialized=False):
        if serialized:
            return [autor.serialize(compact=True) for autor in self.autores.all()]
        return [autor for autor in self.autores.all()]

    def agregar_autor(self, ciudadano):
        self.autores.add(ciudadano)

    def es_autor(self, ciudadano):
        return ciudadano in self.get_autores()

    def voto_a_favor(self, ciudadano):
        return Voto.objects.filter(voto='A', ciudadano=ciudadano, idea=self).count() == 1
    
    def voto_en_contra(self, ciudadano):
        return Voto.objects.filter(voto='N', ciudadano=ciudadano, idea=self).count() == 1

class Categoria(models.Model):
    nombre = models.CharField(max_length=64)

    def serialize(self):
        return {
            'id': self.pk,
            'nombre': self.nombre
        }

    def __str__(self):
        return self.nombre

class VotoEncuesta(models.Model):
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)
    encuesta = models.ForeignKey('Encuesta', on_delete=models.CASCADE)
    opcion = models.ForeignKey('OpcionEncuesta', on_delete=models.CASCADE)

class OpcionEncuesta(models.Model):
    opcion = models.CharField(max_length=128)
    encuesta = models.ForeignKey('Encuesta', on_delete=models.CASCADE)

    def __str__(self):
        return self.encuesta.pregunta + " : " + self.opcion

    def serialize(self, request=None):
        votos = VotoEncuesta.objects.filter(opcion=self).count()
        if request:
            ciudadano = Ciudadano.objects.get(email=request.user.username)
            votada = VotoEncuesta.objects.filter(opcion=self, ciudadano=ciudadano).count() == 1
        else:
            votada = None
        return {
            'id': self.pk,
            'opcion': self.opcion,
            'votos': votos,
            'votada': votada
        }

class Encuesta(models.Model):
    pregunta = models.CharField(max_length=512)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    autor = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)

    def __str__(self):
        return self.pregunta

    def serialize(self, request=None):
        opciones = list(OpcionEncuesta.objects.filter(encuesta=self))
        return {
            'id': self.pk,
            'pregunta': self.pregunta,
            'autor': self.autor.serialize(compact=True),
            'opciones': [opcion.serialize(request=request) for opcion in opciones]
        }

class MergeApproval(models.Model):
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)
    merge = models.ForeignKey('IdeaMerge', on_delete=models.CASCADE)

class IdeaMerge(models.Model):
    ideaA = models.ForeignKey(Idea, on_delete=models.SET_NULL, null=True, related_name='idea_a')
    ideaB = models.ForeignKey(Idea, on_delete=models.SET_NULL, null=True, related_name='idea_b')
    result = models.ForeignKey(Idea, on_delete=models.CASCADE, null=True)
    fecha = models.DateTimeField()

    def calculate_autores(self):
        self.result.autores.clear()
        for autor in self.get_autores():
            self.result.autores.add(autor)


    def get_autores(self):
        autoresA = self.ideaA.get_autores()
        autoresB = self.ideaB.get_autores()
        merge_autores = autoresA
        for autor in autoresB:
            if autor.pk not in [ autorA.pk for autorA in autoresA ]:
                merge_autores.append(autor)
        return merge_autores

    def approvals(self):
        autores = self.get_autores()
        return [ {
            'ciudadano': autor.serialize(compact=True),
            'approved': True if MergeApproval.objects.filter(ciudadano=autor, merge=self).count() == 1 else False
        } for autor in autores ]
    
    def is_approved(self):
        return all([approval['approved'] for approval in self.approvals()])

    def __str__(self):
        return "{} + {} = {}".format(str(self.ideaA), str(self.ideaB), str(self.result))

    def serialize(self, request=None):
        approvals = self.approvals()
        return {
            'id': self.pk,
            'ideaA': self.ideaA.serialize(request=request) if self.ideaA else None,
            'ideaB': self.ideaB.serialize(request=request) if self.ideaB else None,
            'result': self.result.serialize(request=request) if self.result else None,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M'),
            'approvals': approvals,
            'approved': all([approval['approved'] for approval in approvals])
        }

    def already_approved(self, ciudadano):
        approvals = self.approvals()
        return ciudadano.pk in [approval['ciudadano']['id'] for approval in approvals if approval['approved']]

    def add_approval(self, ciudadano):
        if MergeApproval.objects.filter(merge=self, ciudadano=ciudadano).count() == 0:
            new_approval = MergeApproval(merge=self, ciudadano=ciudadano)
            new_approval.save()
        if self.result and self.is_approved():
            self.result.approved = True
            self.result.save()
            self.ideaA.approved = False
            self.ideaA.save()
            self.ideaB.approved = False
            self.ideaB.save()
            ciudadanos_procesados = []
            votos_sumados = list(Voto.objects.filter(idea=self.ideaA)) + list(Voto.objects.filter(idea=self.ideaB))
            for voto in votos_sumados:
                if voto.ciudadano.pk not in ciudadanos_procesados:
                    new_voto = Voto(idea=self.result, ciudadano=voto.ciudadano, voto=voto.voto, comentario=voto.comentario, fecha=voto.fecha)
                    new_voto.save()
                    ciudadanos_procesados.append(voto.ciudadano.pk)
