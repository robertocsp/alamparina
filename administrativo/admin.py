from django.contrib import admin
from administrativo.models import *

# Register your models here.

class AlocacaoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'data_alocacao', 'identificador',)
    list_filter = ('identificador','marca',)
    search_fields = ('marca__nome',)

class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nome','de','ate','no_dias')
    date_hierarchy = 'de'
    ordering = ('de',)

    def no_dias(self,obj):
        return ("%s" % (obj.ate - obj.de))

class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'contato')

class CanalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'percentual_deflacao', 'absoluto_deflacao')

class EspacoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'tipo', 'loja')
    list_filter = ('loja',)

admin.site.register(TipoEspaco)
admin.site.register(Espaco, EspacoAdmin)
admin.site.register(Marca,MarcaAdmin)
admin.site.register(Periodo,PeriodoAdmin)
admin.site.register(Loja)
admin.site.register(Alocacao,AlocacaoAdmin)
admin.site.register(Canal, CanalAdmin)
