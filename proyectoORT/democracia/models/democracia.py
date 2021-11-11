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
    
    def votos_positivos(self):
        return Voto.objects.filter(idea=self, voto='A').count()

    def votos_negativos(self):
        return Voto.objects.filter(idea=self, voto='N').count()

    def total_votos(self):
        return self.votos_negativos() + self.votos_positivos()

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
            'voto_en_contra': voto_en_contra
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