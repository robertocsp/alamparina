from django.contrib import admin
from administrativo.models import TipoEspaco,Espaco,Marca,Periodo,Loja,Alocacao

# Register your models here.

class AlocacaoAdmin(admin.ModelAdmin):
    pass

class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nome','de','ate','no_dias')
    ordering = ('de',)

    def no_dias(self,obj):
        return ("%s" % (obj.ate - obj.de))

class MarcaAdmin(admin.ModelAdmin):
    filter_horizontal = ('user',)

admin.site.register(TipoEspaco)
admin.site.register(Espaco)
admin.site.register(Marca,MarcaAdmin)
admin.site.register(Periodo,PeriodoAdmin)
admin.site.register(Loja)
admin.site.register(Alocacao,AlocacaoAdmin)
