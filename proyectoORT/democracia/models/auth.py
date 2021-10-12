from django.core.exceptions import DisallowedHost
from django.db import models
from django.contrib.auth.models import User

class Ciudadano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=64)
    email = models.CharField(max_length=128, unique=True)
    firebaseId = models.CharField(max_length=128, unique=True)
    perfilUrl = models.CharField(max_length=254, null=True, blank=True)
    dni = models.CharField(max_length=9, default='00000000')
    dniFrontUrl = models.CharField(max_length=254, null=True, blank=True)
    dniBackUrl = models.CharField(max_length=254, null=True, blank=True)
    partido = models.ForeignKey('Partido', on_delete=models.SET_NULL, null=True, default=None)
    distrito = models.ForeignKey('Distrito', on_delete=models.SET_NULL, null=True, default=None)
    verificado = models.BooleanField(default=False)
    legislador = models.BooleanField(default=False)

    def serialize(self):
        return {
            'id': self.pk,
            'nombre': self.nombre,
            'email': self.email,
            'firebaseId': self.firebaseId,
            'perfilUrl': self.perfilUrl,
            'dni': self.dni,
            'dniFrontUrl': self.dniFrontUrl,
            'dniBackUrl': self.dniBackUrl,
            'partido': self.partido.nombre if self.partido else None,
            'distrito': self.distrito.nombre if self.distrito else None,
            'verificado': self.verificado,
            'legislador': self.legislador
        }
    
    def __str__(self):
        return self.nombre