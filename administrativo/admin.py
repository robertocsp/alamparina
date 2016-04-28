from django.contrib import admin
from administrativo.models import *

# Register your models here.

class ContratoAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('data_contrato', 'no_contrato', 'identificador', 'valor', 'percentual_deflacao', 'custo_embalagem', 'custo_entrega', 'marca', 'espaco', 'periodo', 'observacao',)
        }),
    )
    list_display = ('marca', 'no_contrato', 'data_contrato', 'identificador', 'percentual_deflacao', 'custo_embalagem', 'custo_entrega',)
    list_filter = ('identificador','marca',)
    search_fields = ('marca__nome',)

    def espacos_disponiveis(self,obj):
        return Espaco.objects.filter(disponivel=True)

class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nome','de','ate','no_dias')
    date_hierarchy = 'de'
    ordering = ('de',)

    def no_dias(self,obj):
        return ("%s" % (obj.ate - obj.de))

class MarcaAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('nome', 'razao_social', 'cnpj_cpf', 'endereco', 'contato', 'logo', 'user', 'codigo')
        }),
    )
    list_display = ('nome', 'contato')

class CanalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'percentual_deflacao', 'custo_embalagem', 'custo_entrega')

class EspacoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'tipo', 'loja', 'disponivel')
    list_filter = ('loja','disponivel',)

admin.site.register(TipoEspaco)
admin.site.register(Espaco, EspacoAdmin)
admin.site.register(Marca,MarcaAdmin)
admin.site.register(Periodo,PeriodoAdmin)
admin.site.register(Loja)
admin.site.register(Contrato, ContratoAdmin)
admin.site.register(Canal, CanalAdmin)
