from django.contrib import admin
from .models.auth import Ciudadano
from .models.democracia import Partido, Distrito, Idea, Categoria, Voto, Encuesta, VotoEncuesta, OpcionEncuesta

admin.site.register(Ciudadano)
admin.site.register(Partido)
admin.site.register(Distrito)
admin.site.register(Idea)
admin.site.register(Categoria)
admin.site.register(Voto)
admin.site.register(Encuesta)
admin.site.register(VotoEncuesta)
admin.site.register(OpcionEncuesta)
# Register your models here.
