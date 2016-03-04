from django.db import models
from administrativo.models import Marca

# Create your models here.

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=300)
    largura = models.IntegerField()
    altura = models.IntegerField()
    profundidade = models.IntegerField()
    marca = models.ForeignKey(Marca)

    def __unicode__(self):
        return self.nome
