from django.db import models
from administrativo.models import Marca

# Create your models here.

class Produto(models.Model):
    nome = models.CharField('nome', max_length=100)
    descricao = models.CharField('descricao', max_length=300)
    largura = models.IntegerField('largura')
    altura = models.IntegerField('altura')
    profundidade = models.IntegerField('profundidade')
    marca = models.ForeignKey(Marca) #related_name='produtos' => Esta gerando erro no migrations
    quantidade = models.IntegerField('quantidade', blank=True, null=True)

    def __unicode__(self):
        return self.nome

class Checkin(models.Model):
    TIPO = (
        ("chin","CheckIn"),
        ("chout","CheckOut"),
    )
    tipo = models.CharField(max_length=10, choices=TIPO, default="chin")

    STATUS = (
        ("emprocessamento", "EmProcessamento"),
        ("enviado", "Enviado"),
        ("emanalise", "EmAnalise"),
        ("confirmado", "Confirmado"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="emprocessamento")

    marca = models.ForeignKey(Marca, blank=True, null=True)
    #produto = models.ManyToManyField(Produto, through='Expedicao')
    dia_agendamento = models.DateField(auto_now=False,auto_now_add=False)
    hora_agendamento = models.TimeField(auto_now=False,auto_now_add=False)
    observacao = models.TextField(blank=True)

    def __unicode__(self):
        return '%s %s' % (self.dia_agendamento, self.hora_agendamento)

class Expedicao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=False)
    checkin = models.ForeignKey(Checkin, on_delete=models.CASCADE, null=False)
    quantidade = models.IntegerField(blank=True, null=True)

    STATUS = (
        ("ok", "ProdutoOK"),
        ("avariado", "ProdutoAvariado"),
        ("ausente", "Ausente")
    )
    status = models.CharField(max_length=20, choices=STATUS, default="ok")
    observacao = models.TextField(blank=True)

    class Meta:
       unique_together = ('checkin', 'produto')