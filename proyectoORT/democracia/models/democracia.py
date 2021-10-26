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

class Idea(models.Model):
    titulo = models.CharField(max_length=128)
    fechaPublicacion = models.DateTimeField()
    contenido = models.TextField(max_length=1024)
    votosPositivos = models.IntegerField(default=0)
    votosNegativos = models.IntegerField(default=0)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, default=None, blank=True)
    autores = models.ManyToManyField('Ciudadano')
    
    def total_votos(self):
        return self.votosNegativos + self.votosPositivos

    def serialize(self, request=None):
        if request: 
            ciudadano = Ciudadano.objects.get(email=request.user.username)
            es_autor = self.es_autor(ciudadano)
            voto_a_favor = self.voto_a_favor(ciudadano)
            voto_en_contra = self.voto_en_contra(ciudadano)
        else:
            es_autor = None
            voto_a_favor = None
            voto_en_contra = None
        return {
            'id': self.pk,
            'titulo': self.titulo,
            'fechaPublicacion': self.fechaPublicacion.strftime('%Y-%m-%d %H:%M'),
            'contenido': self.contenido,
            'votosPositivos': self.votosPositivos,
            'votosNegativos': self.votosNegativos,
            'categoria': self.categoria.nombre if self.categoria else None,
            'autores': self.get_autores(serialized=True),
            'es_autor': es_autor,
            'voto_a_favor': voto_a_favor,
            'voto_en_contra': voto_en_contra
        }
    
    def __str__(self):
        return "[{}] {} {}/{}".format(self.fechaPublicacion.strftime('%Y-%m-%d %H:%M'), self.titulo, self.votosPositivos, self.votosNegativos)

    def get_autores(self, serialized=False):
        if serialized:
            return [autor.serialize(compact=True) for autor in self.autores.all()]
        return [autor for autor in self.autores.all()]

    def agregar_autor(self, ciudadano):
        self.autores.add(ciudadano)

    def es_autor(self, ciudadano):
        return ciudadano in self.get_autores()

    def voto_a_favor(self, ciudadano):
        return False
    
    def voto_en_contra(self, ciudadano):
        return False

class Categoria(models.Model):
    nombre = models.CharField(max_length=64)

    def serialize(self):
        return {
            'id': self.pk,
            'nombre': self.nombre
        }

    def __str__(self):
        return self.nombre