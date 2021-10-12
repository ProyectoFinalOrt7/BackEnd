from django.contrib import admin
from .models.auth import Ciudadano
from .models.democracia import Partido, Distrito

admin.site.register(Ciudadano)
admin.site.register(Partido)
admin.site.register(Distrito)
# Register your models here.
