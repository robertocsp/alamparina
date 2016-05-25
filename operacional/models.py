# -*- coding: utf-8 -*-
from django.db import models
from administrativo.models import *
import datetime

# Create your models here.

class Produto(models.Model):
    nome = models.CharField('nome', max_length=100)
    codigo = models.CharField('codigo', blank=True, max_length=20)
    descricao = models.CharField('Descricao', max_length=300)
    largura = models.IntegerField('largura')
    altura = models.IntegerField('altura')
    profundidade = models.IntegerField('profundidade')
    marca = models.ForeignKey(Marca) #related_name='produtos' => Esta gerando erro no migrations
    quantidade = models.IntegerField('quantidade', default=0)
    preco_base = models.FloatField('preço base', blank=True, null=True)
    preco_venda = models.FloatField('preço venda', blank=True, null=True)
    miniloja = models.ForeignKey(Miniloja, blank=True, null=True)
    unidade = models.ManyToManyField(Unidade, through='Estoque')
    estoque_minimo = models.IntegerField('Estoque Mínimo', default=0)
    ncm = models.CharField('NCM', max_length=100, blank=True, null=True)
    peso = models.FloatField('peso', blank=True, null=True)
    itens_inclusos = models.CharField('Itens inclusos', max_length=200, blank=True, null=True)
    garantia = models.IntegerField('Garantia', default=0)
    palavras_chaves = models.CharField('Palavras chaves', max_length=200, null=True, blank=True)
    codigo_marca = models.CharField('Descricao', max_length=20, null=True, blank=True)
    UNIDADE_VENDA = (
        ("unidade", "UND (Unidade)"),
        ("pacote", "PCT (Pacote)"),
        ("kit", "Kit (Kit de presentes)"),
    )
    unidade_venda = models.CharField(max_length=15, choices=UNIDADE_VENDA, default="unidade")

    EM_ESTOQUE = (
        ("sim", "Sim"),
        ("nao", "Nao"),
    )
    em_estoque = models.CharField(max_length=5, choices=EM_ESTOQUE, default="nao")

    def __unicode__(self):
        return self.nome

class Checkin(models.Model):
    TIPO = (
        ("chin","CheckIn"),
        ("chout","CheckOut"),
    )
    tipo = models.CharField(max_length=15, choices=TIPO, default="chin")

    STATUS = (
        ("emprocessamento", "EmProcessamento"),
        ("enviado", "Enviado"),
        ("emanalise", "EmAnalise"),
        ("confirmado", "Confirmado"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="emprocessamento")

    marca = models.ForeignKey(Marca, blank=True, null=True)
    produto = models.ManyToManyField(Produto, through='Expedicao')
    dia_agendamento = models.DateField(auto_now=False,auto_now_add=False)
    hora_agendamento = models.TimeField(auto_now=False,auto_now_add=False, null=True)
    observacao = models.TextField(blank=True)
    unidade = models.ForeignKey(Unidade)

    MOTIVO = (
        ("creditarestoque", "CreditarEstoque"),
        ("comprafornecedor", "CompraFornecedor"),
    )
    motivo = models.CharField(max_length=20, choices=MOTIVO, default="creditarestoque")

    canal = models.ManyToManyField(Canal)

    def __unicode__(self):
        return '%s %s' % (self.dia_agendamento, self.hora_agendamento)

    def status_enviado(self):
        return "enviado"

    def status_emprocessamento(self):
        return "emprocessamento"

    def status_emanalise(self):
        return "emanalise"

    def status_confirmado(self):
        return "confirmado"

    def motivo_creditar_estoque(self):
        return 'creditarestoque'

    def motivo_compra_fornecedor(self):
        return 'comprafornecedor'

'''
    def clean(self):
        if self.dia_agendamento < datetime.datetime(2016, 03, 01):
            raise ValidationError ('data menor que atual')

    def save(self, *args, **kwargs):
        self.clean()
        super(Checkin, self).save(*args, **kwargs)
'''
class Expedicao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=False)
    checkin = models.ForeignKey(Checkin, on_delete=models.CASCADE, null=False)
    quantidade = models.IntegerField()

    STATUS = (
        ("ok", "ProdutoOK"),
        ("avariado", "ProdutoAvariado"),
        ("ausente", "Ausente")
    )
    status = models.CharField(max_length=20, choices=STATUS, blank=True, null=True)
    observacao = models.TextField(blank=True)
    gravou_estoque = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
       unique_together = ('checkin', 'produto')

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, null=False)
    unidade = models.ForeignKey(Unidade, null=False)
    quantidade = models.IntegerField()

    class Meta:
       unique_together = ('produto', 'unidade')

class Checkout(models.Model):
    MOTIVO = (
        ("emprestimo", "Emprestimo"),
        ("consignacao", "Consignacao"),
        ("avaria", "Avaria"),
        ("venda", "Venda"),
    )
    motivo = models.CharField(max_length=20, choices=MOTIVO)

    STATUS = (
        ("emprocessamento", "EmProcessamento"),
        ("confirmado", "Confirmado"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="emprocessamento")

    dia = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)
    marca = models.ForeignKey(Marca, blank=True, null=True)

    FORMAPAGAMENTO = (
        ("credito", "Crédito"),
        ("debito", "Débito"),
        ("dinheiro", "Dinheiro"),
        ("cheque", "Cheque"),
    )

    formapagamento = models.CharField(max_length=20, choices=FORMAPAGAMENTO, blank=True, null=True)
    unidade = models.ForeignKey(Unidade)
    produto = models.ForeignKey(Produto, blank=True, null=True)
    cliente_unidade = models.ForeignKey(Cliente_Unidade, blank=True, null=True)
    canal = models.ForeignKey(Canal, blank=True, null=True)
    periodo = models.ForeignKey(Periodo, blank=True, null=True)
    dtrealizado = models.DateField(blank=True, null=True)
    quantidade = models.IntegerField()
    preco_venda = models.FloatField('preço venda', blank=True, null=True)
    def __unicode__(self):
        return '%s %s' % (self.motivo, self.dia)

    def motivo_emprestimo(self):
        return 'emprestimo'

    def motivo_consignacao(self):
        return 'consignacao'

    def motivo_avaria(self):
        return 'avaria'

    def motivo_venda(self):
        return 'venda'


class Recomendacao(models.Model):
    nome = models.CharField('nome', max_length=100, null=False)
    email = models.CharField('email', max_length=30, blank=True)
    website = models.CharField('website', max_length=30, blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    comentario = models.CharField('comentario', max_length=200, blank=True)
    marca = models.ForeignKey(Marca)

class ItemVenda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=False)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, null=False)
    quantidade = models.IntegerField()

    # não vou implementar o status. Deverá ser utilizado como devolução, retorno de venda.
    STATUS = (
        ("ok", "ProdutoOK"),
        ("avariado", "ProdutoAvariado"),
        ("ausente", "Ausente")
    )
    status = models.CharField(max_length=20, choices=STATUS, blank=True, null=True)
    preco_venda = models.FloatField()
    observacao = models.TextField(blank=True)
    gravou_estoque = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
       unique_together = ('checkout', 'produto')
