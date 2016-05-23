from django.contrib import admin
from operacional.models import *

# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ( 'codigo', 'nome','marca','cubagem','quantidade','preco_venda','marca', 'miniloja')
    list_filter = ('marca', 'miniloja',)
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

class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'marca', 'unidade', 'quantidade',)
    list_filter = ('produto', 'unidade', 'produto__marca__nome')

    def marca(self,obj):
        return obj.produto.marca

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('dia', 'motivo', 'unidade')
    list_filter = ('motivo', 'unidade')
    date_hierarchy = 'dia'
    ordering = ('dia',)

class RecomendacaoAdmin(admin.ModelAdmin):
    list_display = ('marca','nome','email')
    list_filter = ('marca' ,)

class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('produto','checkout',)
    list_filter = ('produto', 'checkout',)

admin.site.register(Produto,ProdutoAdmin)
admin.site.register(Checkin,CheckinAdmin)
admin.site.register(Expedicao,ExpedicaoAdmin)
admin.site.register(ItemVenda, ItemVendaAdmin)
admin.site.register(Estoque,EstoqueAdmin)
admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Recomendacao, RecomendacaoAdmin)
