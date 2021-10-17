from django.db import models

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
    
    def total_votos(self):
        return self.votosNegativos + self.votosPositivos

    def serialize(self):
        return {
            'id': self.pk,
            'titulo': self.titulo,
            'fechaPublicacion': self.fechaPublicacion.strftime('%Y-%m-%d %H:%M'),
            'contenido': self.contenido,
            'votosPositivos': self.votosPositivos,
            'votosNegativos': self.votosNegativos,
            'categoria': self.categoria.serialize() if self.categoria else None
        }

class Categoria(models.Model):
    nombre = models.CharField(max_length=64)

    def serialize(self):
        return self.nombre