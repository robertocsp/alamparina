from django.db import models
from django.contrib.auth.models import User
from django.core import serializers


# Create your models here.

class Unidade(models.Model):
    nome = models.CharField(max_length=50)
    endereco = models.CharField(max_length=100)

    def __unicode__(self):
        return self.nome

    def get_unidades_marca(self, marca):
        return self.objects.filter(miniloja__contrato__marca=marca).distinct()

class Marca(models.Model):
    nome = models.CharField(max_length=50)
    razao_social = models.CharField(max_length=100)
    cnpj_cpf = models.IntegerField()
    endereco = models.CharField(max_length=100)
    contato = models.CharField(max_length=100,blank=True)
    logo = models.ImageField(upload_to='/var/www/html/logos',height_field=None,width_field=None,max_length=100,blank=True)
    user = models.ManyToManyField(User,blank=True,null=True,related_name="marca")
    codigo = models.CharField(max_length=5, blank=True)
    sequencial_atual = models.IntegerField(default=0)

    def __unicode__(self):
        return self.nome

class TipoMiniloja(models.Model):
    largura = models.IntegerField()
    altura = models.IntegerField()
    profundidade = models.IntegerField()
    tipo = models.CharField(max_length=10)
    preco = models.FloatField()
    volume = None
    def __unicode__(self):
        return self.tipo

class Miniloja(models.Model):
    identificador = models.CharField(max_length=20)
    tipo = models.ForeignKey(TipoMiniloja)
    unidade = models.ForeignKey(Unidade, blank=True, null=True, related_name='miniloja')
    disponivel = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s %s' % (self.identificador, self.tipo)


class Periodo(models.Model):
    nome = models.CharField(max_length=30)
    de = models.DateField(auto_now=False,auto_now_add=False)
    ate = models.DateField(auto_now=False,auto_now_add=False)
    pagamento_de = models.DateField(blank=True, null=True)
    pagamento_ate = models.DateField(blank=True, null=True)
    def __unicode__(self):
        return self.nome

class Contrato(models.Model):
    no_contrato = models.CharField('no_contrato', max_length=30)
    data_contrato = models.DateField()
    valor = models.FloatField(blank=True, null=True)
    identificador = models.CharField(max_length=20, blank=True)
    marca = models.ForeignKey(Marca)
    miniloja = models.ManyToManyField(Miniloja, related_name='contrato')
    periodo = models.ManyToManyField(Periodo)
    percentual_deflacao = models.FloatField()
    custo_embalagem = models.IntegerField()
    custo_entrega = models.IntegerField()
    observacao = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.marca, self.periodo, self.miniloja)


def __unicode__(self):
        return self.marca.nome

class Canal(models.Model):
    nome = models.CharField('Nome', max_length=30)
    percentual_deflacao = models.FloatField(blank=True, null=True)
    custo_embalagem = models.IntegerField(blank=True, null=True)
    custo_entrega = models.IntegerField(blank=True, null=True)
    acumulativo = models.BooleanField(default=False)

    TIPO = (
        ("unidade","Unidade"),
        ("catalogo","Catalogo"),
        ("ecommerce", "Ecommerce"),
        ("revenda", "Revenda"),
    )
    tipo = models.CharField(max_length=15, choices=TIPO, default="unidade")

    def __unicode__(self):
        return self.nome