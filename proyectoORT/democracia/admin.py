from django.contrib import admin
from .models.auth import Ciudadano
from .models.democracia import Partido, Distrito, Idea, Categoria

admin.site.register(Ciudadano)
admin.site.register(Partido)
admin.site.register(Distrito)
admin.site.register(Idea)
admin.site.register(Categoria)
# Register your models here.
