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

class Checkin(models.Model):
    TIPO = (
        ("chin","CheckIn"),
        ("chout","CheckOut"),
    )
    tipo = models.CharField(max_length=10, choices=TIPO, default="chin")

    STATUS = (
        ("enviado","Enviado"),
        ("emanalise", "Emanalise"),
        ("confirmado","Confirmado"),
    )
    status = models.CharField(max_length=10, choices=STATUS, default="enviado")
    produto = models.ManyToManyField(Produto, through='Expedicao')
    dia_agendamento = models.DateField(auto_now=False,auto_now_add=False)
    hora_agendamento = models.TimeField(auto_now=False,auto_now_add=False)

class Expedicao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    checkin = models.ForeignKey(Checkin, on_delete=models.CASCADE)
    quantidade = models.IntegerField(blank=False)




