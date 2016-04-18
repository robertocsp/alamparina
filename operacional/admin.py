from django.contrib import admin
from operacional.models import *

# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome','marca','cubagem','quantidade','preco_venda','marca', 'espaco')
    list_filter = ('marca', 'espaco',)
    search_fields = ('marca',)

    def cubagem(self,obj):
        return (obj.altura * obj.largura * obj.profundidade)

class CheckinAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'marca', 'status', 'dia_agendamento', 'hora_agendamento',)
    list_filter = ('tipo', 'marca', 'status',)
    search_fields = ('marca__nome',)

class ExpedicaoAdmin(admin.ModelAdmin):
    list_display = ('produto','tipo_checkinout', 'data_checkinout',)
    list_filter = ('checkin__tipo', 'checkin__dia_agendamento',)

    def tipo_checkinout(self,obj):
        return obj.checkin.tipo

    def data_checkinout(self,obj):
        return obj.checkin.dia_agendamento

class Estoque_LojaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'marca', 'loja', 'quantidade',)
    list_filter = ('produto', 'loja', 'produto__marca__nome')

    def marca(self,obj):
        return obj.produto.marca


admin.site.register(Produto,ProdutoAdmin)
admin.site.register(Checkin,CheckinAdmin)
admin.site.register(Expedicao,ExpedicaoAdmin)
admin.site.register(Estoque_Loja,Estoque_LojaAdmin)
