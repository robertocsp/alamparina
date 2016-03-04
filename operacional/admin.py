from django.contrib import admin
from django import forms
from operacional.models import Produto
from administrativo.models import Marca

# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome','marca')


admin.site.register(Produto,ProdutoAdmin)
