from django.core.exceptions import DisallowedHost
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest, ObjectDoesNotExist

class Ciudadano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=64)
    email = models.CharField(max_length=128, unique=True)
    firebaseId = models.CharField(max_length=128, unique=True, null=True, blank=True, default=None)
    perfilUrl = models.CharField(max_length=254, null=True, blank=True)
    dni = models.CharField(max_length=9, default='00000000')
    dniFrontUrl = models.CharField(max_length=254, null=True, blank=True)
    dniBackUrl = models.CharField(max_length=254, null=True, blank=True)
    partido = models.ForeignKey('Partido', on_delete=models.SET_NULL, null=True, default=None)
    distrito = models.ForeignKey('Distrito', on_delete=models.SET_NULL, null=True, default=None)
    verificado = models.BooleanField(default=False)
    legislador = models.BooleanField(default=False)

    def serialize(self, compact=False):
        if compact:
            return {
            'id': self.pk,
            'nombre': self.nombre,
            'legislador': self.legislador
        }
        return {
            'id': self.pk,
            'nombre': self.nombre,
            'email': self.email,
            'firebaseId': self.firebaseId,
            'perfilUrl': self.perfilUrl,
            'dni': self.dni,
            'partido': self.partido.nombre if self.partido else None,
            'distrito': self.distrito.nombre if self.distrito else None,
            'verificado': self.verificado,
            'legislador': self.legislador
        }
    
    def __str__(self):
        return "{} ({})".format(self.nombre, self.dni)

    @classmethod
    def register_new(cls, register_data):
        required_fields = ['nombre', 'email', 'dni', 'password']
        if not all([key in register_data.keys() for key in required_fields]):
            raise BadRequest('Missing required field. Required: {}'.format(required_fields))

        try:
            User.objects.get(username=register_data['email'])
            raise BadRequest('User with email {} already registered'.format(register_data['email']))
        except ObjectDoesNotExist:
            pass
        
        new_user = User.objects.create_user(register_data['email'], register_data['email'], register_data['password'])
        new_user.save()
        new_ciudadano = cls(nombre = register_data['nombre'], email = register_data['email'], dni = register_data['dni'], user = new_user)
        new_ciudadano.save()
        return new_ciudadano