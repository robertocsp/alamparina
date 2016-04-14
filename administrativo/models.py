from django.db import models
from django.contrib.auth.models import User
from django.core import serializers


# Create your models here.

class Loja(models.Model):
    nome = models.CharField(max_length=50)
    endereco = models.CharField(max_length=100)
    percentual_deflacao = models.FloatField(blank=True, null=True)
    absoluto_deflacao = models.IntegerField(blank=True,null=True)

    def __unicode__(self):
        return self.nome

class Marca(models.Model):
    nome = models.CharField(max_length=50)
    razao_social = models.CharField(max_length=100)
    cnpj_cpf = models.IntegerField()
    endereco = models.CharField(max_length=100)
    contato = models.CharField(max_length=100,blank=True)
    logo = models.ImageField(upload_to='/var/www/html/logos',height_field=None,width_field=None,max_length=100,blank=True)
    user = models.ManyToManyField(User,blank=True,null=True,related_name="marca")

    def __unicode__(self):
        return self.nome

class TipoEspaco(models.Model):
    largura = models.IntegerField()
    altura = models.IntegerField()
    profundidade = models.IntegerField()
    tipo = models.CharField(max_length=10)
    preco = models.FloatField()

    def __unicode__(self):
        return self.tipo

class Espaco(models.Model):
    identificador = models.CharField(max_length=20)
    tipo = models.ForeignKey(TipoEspaco)
    loja = models.ForeignKey(Loja, blank=True, null=True)

    def __unicode__(self):
        return u'%s %s' % (self.identificador, self.tipo)


class Periodo(models.Model):
    nome = models.CharField(max_length=30)
    de = models.DateField(auto_now=False,auto_now_add=False)
    ate = models.DateField(auto_now=False,auto_now_add=False)

    def __unicode__(self):
        return self.nome

class Alocacao(models.Model):
    data_alocacao = models.DateField()
    identificador = models.CharField(max_length=20, blank=True)
    marca = models.ForeignKey(Marca)
    espaco = models.ManyToManyField(Espaco, related_name='alocacao')
    periodo = models.ManyToManyField(Periodo)

    def __unicode__(self):
        return self.marca.nome

class Canal(models.Model):
    nome = models.CharField('Nome', max_length=30)
    percentual_deflacao = models.FloatField()
    absoluto_deflacao = models.IntegerField()
    acumulativo = models.BooleanField(default=False)

    TIPO = (
        ("loja","Loja"),
        ("catalogo","Catalogo"),
        ("ecommerce", "Ecommerce"),
        ("revenda", "Revenda"),
    )
    tipo = models.CharField(max_length=15, choices=TIPO, default="loja")

    precificacao = None
    def __unicode__(self):
        return self.nome