from django.contrib import admin
from operacional.models import Produto, Checkin, Expedicao

# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome','marca')

class CheckinAdmin(admin.ModelAdmin):
    list_display = ('tipo','status','dia_agendamento','hora_agendamento')

class ExpedicaoAadmin(admin.ModelAdmin):
    pass
admin.site.register(Produto,ProdutoAdmin)
admin.site.register(Checkin,CheckinAdmin)
admin.site.register(Expedicao,ExpedicaoAadmin)
