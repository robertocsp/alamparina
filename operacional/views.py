# -*- coding: utf-8 -*-
from resource import error

from boto.ecs import item
from botocore.vendored.requests.api import request
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.lookups import Exact
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import views
from django.db import transaction
from django.template.context_processors import request
from django.utils import *
from django.shortcuts import get_object_or_404
from administrativo.models import *
from models import Canal
from models import Produto
from models import Recomendacao
from operacional.forms import *
from django.core.files import File

# Create your views here.
from alamparina.library import memoriacalculo
from alamparina.library import acesso
import datetime
import time
import xlrd
import codecs
import json

#view ajax
def get_prod(request):
    q = request.GET.get('term', '')
    u = request.GET.get('unidade', '')
    if u.endswith('/'):
        u = u[:-1]
    estoque_list = Estoque.objects.filter(unidade_id=u)
    results = []
    for estoque in estoque_list:
        prods = Produto.objects.filter(id=estoque.produto_id, nome__icontains=q)
        for prod in prods:
            prods_data = {}
            prods_data["label"] = prod.nome + " - " + prod.marca.nome
            prods_data["value"] = prod.id
            results.append(prods_data)

    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def get_prod_marca(request):
    q = request.GET.get('term', '')
    u = request.GET.get('unidade', '')
    m = request.GET.get('marca', '')
    if u.endswith('/'):
        u = u[:-1]
    if m.endswith('/'):
        m = m[:-1]

    estoque_list = Estoque.objects.filter(unidade_id=u)
    results = []
    for estoque in estoque_list:
        prods = Produto.objects.filter(id=estoque.produto_id, marca=m, nome__icontains=q)
        for prod in prods:
            prods_data = {}
            prods_data["label"] = prod.nome + " - " + prod.marca.nome
            prods_data["value"] = prod.id
            results.append(prods_data)

    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


# a ideia e fazer um login unico verificando se e marca ou operacao
def login_geral(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            # No caso abaixo se o username nao existir ele atribui valor vazio, este caso e mais valido para metodo GET
            # username = request.POST.get('username','')
            senha = request.POST['senha']
            user = authenticate(username=username, password=senha)
            if user != None:
                login(request, user)
                if user.groups.filter(name='marca').count() != 0:
                    marca = Marca.objects.get(user=request.user)
                    request.session['marca_id'] = marca.id
                    return HttpResponseRedirect('/marca/dashboard/')
                else:
                    return HttpResponseRedirect('/operacional/dashboard/')
            else:
                return render(request, 'login_marca.html', {'form': form, 'error': True})
        else:
            raise forms.ValidationError("Algum nome ou id incoerrente com o formulario")
    else:
        form = LoginForm()
        return render(request, 'login_marca.html', {'form': form, 'error': False})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def lista_produtos(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    # produto_list = Produto.objects.filter(marca__id=marca.id)
    produto_list = marca.produto_set.all()
    return render(request, 'lista_produtos.html', {'produto_list': produto_list, 'marca': marca})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def lista_produtos_operacional(request):
    produto_list = Produto.objects.all().order_by('marca')
    marca_list = Marca.objects.all().order_by('nome')
    marca_retorno = None
    if request.method == 'POST':
        if "marca" in request.POST:
            produto_list = Produto.objects.filter(marca=request.POST['marca']).order_by('codigo')
            marca_retorno = Marca.objects.get(id=request.POST['marca'])

    return render(request, 'lista_produtos_operacional.html', {
        'produto_list': produto_list,
        'marca_list': marca_list,
        'marca_retorno': marca_retorno
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def cadastra_produto(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    error = ''
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.marca = marca
            # jogar pra dentro do models
            # mas vou precisar salvar marca
            produto.codigo = marca.codigo.strip() + str(int(marca.sequencial_atual or 0) + 1).zfill(4)
            produto.status = 'ativo'
            produto.save()
            marca.sequencial_atual = int(marca.sequencial_atual) + 1
            marca.save()
            produto_cadastrado = True
            return HttpResponseRedirect(reverse('marca_cadastra_produto'), {'produto_cadastrado': produto_cadastrado})

    else:
        form = ProdutoForm()
    return render(request, 'marca_cadastra_produto.html', {'form': form, 'marca': marca, 'error': error})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def edita_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    erro_acesso = acesso.ValidaAcesso(request, produto.marca)
    error = ''
    if not erro_acesso:
        marca = Marca.objects.get(id=request.session['marca_id'])
        if request.method == 'POST':
            form = ProdutoForm(request.POST, instance=produto)
            if form.is_valid():
                # jogar pra dentro do models
                # mas vou precisar salvar marca
                # produto.codigo= marca.codigo.strip() + str(int(marca.sequencial_atual or 0)+1).zfill(4)
                produto.status = 'ativo'
                produto.save()
                marca.save()

                return render(request, 'marca_cadastra_produto.html',
                              {'form': form, 'marca': marca, 'produto_cadastrado': True, 'error': error})

        else:
            form = ProdutoForm(instance=produto)
        return render(request, 'marca_cadastra_produto.html', {'form': form, 'marca': marca, 'error': error})
    else:
        return render(request, 'acesso-negado.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def lista_checkin(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    checkin_list = Checkin.objects.filter(marca__id=marca.id).order_by('-dia_agendamento')
    return render(request, 'lista_checkin.html', {'checkin_list': checkin_list, 'marca': marca})


# funções inicia_checkin e edita_checkin
def adicionar_canal(lcheckin, lrequest):
    lcheckin.dia_agendamento = datetime.datetime.strptime(lrequest.POST['dia_agendamento'], '%d/%m/%Y')
    lcheckin.save()
    lcheckin.canal.add(Canal.objects.get(id=lrequest.POST['canal']))


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def inicia_checkin(request):
    checkin = Checkin()
    checkin.tipo = 'chin'
    checkin.marca = Marca.objects.get(id=request.session['marca_id'])
    checkin.status = 'emprocessamento'
    cubagem_contratada = 0
    cubagem_empenhada = 0
    saldo_cubagem_estoque = 0
    saldo_cubagem = 0
    expedicao_list = None
    contrato_list = None
    contrato = None
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=checkin.marca).distinct()
    if len(request.POST) == 0 or request.POST['unidade'] == '':
        miniloja_list = None
        canal_list = None
        produto_list = None
        unidade_retorno = None
        canal_retorno = None
    else:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
        checkin.unidade_id = request.POST['unidade']
        miniloja_list = Miniloja.objects.filter(contrato__marca=checkin.marca,
                                                unidade_id=request.POST['unidade']).distinct()
        canal_list = Canal.objects.all()
        cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, unidade_retorno)
        cubagem_empenhada = memoriacalculo.CubagemEmpenhada(checkin.marca, unidade_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(checkin.marca, unidade_retorno)
        saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque - cubagem_empenhada
        expedicao = Expedicao()
        produto_list = checkin.marca.produto_set.all()
        contrato_list = Contrato.objects.filter(marca=checkin.marca, miniloja__unidade=unidade_retorno)
        if contrato_list.count() != 0:
            contrato = contrato_list[0]

    if "adicionar_canal" in request.POST:
        adicionar_canal(checkin, request)
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "remover_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.save()
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "adicionar_produto" in request.POST:
        if "qtde_produto" in request.POST and request.POST['qtde_produto'] != '0' and request.POST[
            'qtde_produto'] != '' and "produtos" in request.POST and request.POST['produtos'] != 'Produtos...':
            checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
            produto = Produto.objects.get(id=request.POST['produtos'])
            expedicao.quantidade = request.POST['qtde_produto']
            expedicao.produto = produto
            expedicao.checkin = checkin
            volume_produto = float(expedicao.quantidade or 0) * float(produto.profundidade or 0) * float(
                produto.largura or 0) * float(produto.altura or 0)
            if volume_produto <= saldo_cubagem:
                checkin.save()
                expedicao.save()
                return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))
            else:
                messages.error(request, 'Volume informado excede saldo contratado disponível')
        else:
            messages.error(request, 'Não existe nenhum produto inserido')

    elif "remover_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        checkin.save()
        expedicao.produto = produto
        expedicao.checkin = checkin
        expedicao.save()
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "finalizar" in request.POST:
        messages.error(request, 'Não existe nenhum produto inserido')

    return render(request, 'checkin.html',
                  {
                      'marca': checkin.marca,
                      'checkin': checkin,
                      'miniloja_list': miniloja_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'cubagem_contratada': cubagem_contratada,
                      'cubagem_empenhada': cubagem_empenhada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                      'unidade_list': unidade_list,
                      'unidade_retorno': unidade_retorno,
                      'contrato': contrato,
                      'inicia': True,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def edita_checkin(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    erro = acesso.ValidaAcesso(request, checkin.marca)
    if not erro:
        expedicao = Expedicao()

        if len(request.POST) != 0:
            unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
            canal_retorno = Canal.objects.get(id=request.POST['canal'])
            checkin.unidade_id = request.POST['unidade']
        else:
            unidade_retorno = Unidade.objects.get(id=checkin.unidade_id)
            canal_retorno_list = Canal.objects.filter(checkin=checkin)
            if canal_retorno_list.count() != 0:
                canal_retorno = canal_retorno_list[0]
            else:
                canal_retorno = None

        expedicao_list = Expedicao.objects.filter(checkin=checkin)

        unidade_list = Unidade.objects.filter(miniloja__contrato__marca=checkin.marca).distinct()
        canal_list = Canal.objects.all()
        contrato_list = Contrato.objects.filter(marca=checkin.marca, miniloja__unidade=unidade_retorno)
        if contrato_list.count() != 0:
            contrato = contrato_list[0]
        else:
            contrato = None

        miniloja_list = Miniloja.objects.filter(contrato__marca=checkin.marca, unidade_id=checkin.unidade_id).distinct()
        produto_list = checkin.marca.produto_set.all()

        if "adicionar_canal" in request.POST:
            adicionar_canal(checkin, request)

        elif "remover_canal" in request.POST:
            checkin.canal.remove(Canal.objects.get(id=request.POST['canal']))
            checkin.save()

        elif "adicionar_produto" in request.POST:
            if "qtde_produto" in request.POST and request.POST['qtde_produto'] != '0' and request.POST[
                'qtde_produto'] != '' and "produtos" in request.POST and request.POST['produtos'] != 'Produtos...':

                checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
                produto = Produto.objects.get(id=request.POST['produtos'])
                expedicao.quantidade = request.POST['qtde_produto']
                expedicao.produto = produto
                expedicao.checkin = checkin
                volume_produto = float(expedicao.quantidade or 0) * float(produto.profundidade or 0) * float(
                    produto.largura or 0) * float(produto.altura or 0)
                cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, unidade_retorno)
                saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(checkin.marca, unidade_retorno)
                cubagem_empenhada = memoriacalculo.CubagemEmpenhada(checkin.marca, unidade_retorno)
                saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque - cubagem_empenhada
                if volume_produto <= saldo_cubagem:
                    checkin.save()
                    expedicao.save()
                else:
                    messages.error(request, '*** Volume informado excede saldo contratado disponível.')

            else:
                messages.error(request, '*** Não existe nenhum produto inserido')

        elif "remover_produto" in request.POST:

            produto = Produto.objects.get(id=request.POST['produtos'])
            expedicao_remove = Expedicao.objects.filter(checkin=checkin, produto=produto)
            if expedicao_remove:  # ajeitar urgente esse expedicao_remove. Faço FILTER para testar para null, se for not null, faço um get.. :/
                expedicao_remove = Expedicao.objects.get(checkin=checkin, produto=produto)
                if expedicao_remove.quantidade > int(request.POST['qtde_produto']):
                    expedicao_remove.quantidade -= int(request.POST['qtde_produto'])
                    expedicao_remove.save()
                    checkin.save()
                elif expedicao_remove.quantidade == int(request.POST['qtde_produto']):
                    expedicao_remove.delete()
                    checkin.save()

        elif "finalizar" in request.POST:
            if expedicao_list == None:
                messages.error(request, '*** Não existe nenhum produto inserido')
            else:
                checkin.status = checkin.status_enviado()
                checkin.save()

        cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, unidade_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(checkin.marca, unidade_retorno)
        cubagem_empenhada = memoriacalculo.CubagemEmpenhada(checkin.marca, unidade_retorno)
        saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque - cubagem_empenhada

        return render(request, 'checkin.html',
                      {
                          'marca': checkin.marca,
                          'checkin': checkin,
                          'miniloja_list': miniloja_list,
                          'canal_list': canal_list,
                          'canal_retorno': canal_retorno,
                          'produto_list': produto_list,
                          'expedicao_list': expedicao_list,
                          'cubagem_contratada': cubagem_contratada,
                          'cubagem_empenhada': cubagem_empenhada,
                          'saldo_cubagem_estoque': saldo_cubagem_estoque,
                          'saldo_cubagem': saldo_cubagem,
                          'unidade_list': unidade_list,
                          'unidade_retorno': unidade_retorno,
                          'contrato': contrato,
                          'inicia': False,

                      }
                      )
    else:
        return render(request, 'acesso-negado.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def dashboard_marca(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    venda_list = Checkout.objects.filter(motivo='venda', marca=marca)
    total_venda = 0
    total_venda_periodo = 0
    total_a_receber_periodo = 0
    periodo_atual = None
    venda_grafico = [[]]

    itemvenda_list = ItemVenda.objects.filter(checkout__status='confirmado', produto__marca=marca)
    for itemvenda in itemvenda_list:
        total_venda += itemvenda.quantidade

    data_hoje = time.strftime("%Y-%m-%d")
    periodo_list = Periodo.objects.filter(ate__gte=data_hoje, de__lte=data_hoje)  # é invertido mesmo.
    for periodo in periodo_list:
        periodo_atual = periodo
        vendaperiodo_list = ItemVenda.objects.filter(checkout__status='confirmado', produto__marca=marca,
                                                     checkout__dtrealizado__range=[periodo.de, periodo.ate])
        for vendaperiodo in vendaperiodo_list:
            total_venda_periodo += vendaperiodo.quantidade
            # preciso obter o contrato da venda (row do queryset Checkout)
            contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=vendaperiodo.checkout.unidade)
            if contrato_list.count() != 0:
                contrato = contrato_list[0]
                total_a_receber_periodo += float(memoriacalculo.PrecoReceber(vendaperiodo, contrato) or 0) * (
                float(vendaperiodo.quantidade) or 0)
            else:
                contrato = None

    produtos_em_estoque = 0
    estoque_list = Estoque.objects.filter(produto__marca=marca)
    for estoque in estoque_list:
        produtos_em_estoque += estoque.quantidade

    periodo_list = Periodo.objects.filter(de__lte=data_hoje).order_by('-de')
    venda_valor_grafico = [[0 for i in xrange(2)] for i in xrange(6)]
    j = 5;
    for periodo in periodo_list:
        venda_valor_grafico[j][0] = 'De ' + periodo.de.strftime("%d-%m-%y") + ' Até ' + periodo.ate.strftime("%d-%m-%y")
        vendaperiodo_list = ItemVenda.objects.filter(checkout__status='confirmado', produto__marca=marca,
                                                     checkout__dtrealizado__range=[periodo.de, periodo.ate])
        preco_venda_periodo = 0
        for vendaperiodo in vendaperiodo_list:
            preco_venda_periodo += float(vendaperiodo.preco_venda or 0) * float(vendaperiodo.quantidade or 0)
        venda_valor_grafico[j][1] = preco_venda_periodo
        if j == 0:
            break
        j -= 1

    cubagem_contratada_periodo = 0
    contrato_list = Contrato.objects.filter(marca=marca, periodo=periodo_atual)
    for contrato in contrato_list:
        cubagem_contratada_periodo += memoriacalculo.CubagemContrato(contrato)

    saldo_cubagem_estoque = 0
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca).distinct()
    for unidade in unidade_list:
        saldo_cubagem_estoque += memoriacalculo.SaldoCubagemEstoqueUnidade(marca, unidade)

    saldo_cubagem_contratada_periodo = cubagem_contratada_periodo - saldo_cubagem_estoque
    ultimasvendas_list = ItemVenda.objects.filter(checkout__status='confirmado', produto__marca=marca).order_by(
        '-checkout__dtrealizado')
    # ultimasvendas_list = Checkout.objects.filter(motivo='venda', marca=marca).order_by('-dtrealizado')
    venda = [[0 for i in xrange(5)] for i in xrange(6)]
    j = 0
    for ultimasvendas in ultimasvendas_list:
        venda[0][j] = ultimasvendas.produto.nome
        venda[1][j] = ultimasvendas.checkout.dtrealizado
        venda[2][j] = "%.2f" % round(ultimasvendas.preco_venda, 2)
        venda[3][j] = ultimasvendas.quantidade
        # todo o lance do contrato ta confuso.
        contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=ultimasvendas.checkout.unidade)
        if contrato_list.count() != 0:
            contrato = contrato_list[0]
            desconto_unidade = ultimasvendas.preco_venda - memoriacalculo.PrecoReceber(ultimasvendas, contrato)
            valor_unidade_liquido = memoriacalculo.PrecoReceber(ultimasvendas, contrato)
            desconto_total = desconto_unidade * venda[3][j]
            valor_total = valor_unidade_liquido * venda[3][j]
            venda[4][j] = "%.2f" % round(desconto_total, 2)
            venda[5][j] = "%.2f" % round(valor_total, 2)
        else:
            venda[4][j] = 'erro!'
            venda[5][j] = 'erro!'
        j += 1
        if j == 5:
            break

    quantidade_produtos_checkin = 0
    quantidade_produtos_devolvidos = 0
    checkin_list = Checkin.objects.filter(marca=marca, status='enviado')
    for checkin in checkin_list:
        expedicao_list = Expedicao.objects.filter(checkin=checkin)
        for expedicao in expedicao_list:
            quantidade_produtos_checkin += expedicao.quantidade
            if expedicao.status == 'avariado' or expedicao.status == 'ausente':
                quantidade_produtos_devolvidos += expedicao.quantidade
    # anterior
    unidade_retorno = None
    periodo_list = None
    periodo_retorno = None
    venda_list = None
    contrato = None
    data_ultima_venda = datetime.date(2000, 01, 01)
    total_pecas_vendidas = 0
    total_vendas = 0.0
    total_a_receber = 0.0
    venda_grafico = [[]]
    venda_produto = [[]]
    venda_grafico_dia = []
    venda_grafico_valor = []
    if len(request.POST) != 0:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])

        if "periodo" in request.POST and request.POST['periodo'] != '':
            periodo_retorno = Periodo.objects.get(id=request.POST['periodo'])
        # periodo
        periodo_list = Periodo.objects.all()
        # venda (groupby produto, sum(qtd))
        if periodo_retorno != None:
            contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=unidade_retorno)
            if contrato_list.count() != 0:
                contrato = contrato_list[0]
            else:
                contrato = None
            venda_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca,
                                                 dtrealizado__range=[periodo_retorno.de, periodo_retorno.ate])
            if venda_list.count() != 0:
                data_ultima_venda = datetime.date(2000, 01, 01)
                for venda in venda_list:
                    if venda.dtrealizado > data_ultima_venda:
                        data_ultima_venda = venda.dtrealizado
                    total_pecas_vendidas += venda.quantidade
                    total_vendas += float(venda.quantidade or 0) * float(venda.preco_venda or 0)
                    total_a_receber += float(memoriacalculo.PrecoReceber(venda, contrato) or 0) * float(
                        venda.quantidade or 0)
            # vendaPorProduto
            codigo = ''
            vendaproduto_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca,
                                                        dtrealizado__range=[periodo_retorno.de,
                                                                            periodo_retorno.ate]).order_by(
                'produto__codigo')
            # vou precisar limpar
            venda_produto = [[0 for i in xrange(5)] for i in xrange(vendaproduto_list.count())]
            j = 0
            for vendaproduto in vendaproduto_list:
                if codigo != vendaproduto.produto.codigo:
                    # zero as variaveis
                    venda_produto[j][0] = vendaproduto.produto.codigo
                    venda_produto[j][1] = vendaproduto.produto.nome
                    venda_produto[j][2] = float(vendaproduto.preco_venda or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[j][3] = float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0) * float(
                        vendaproduto.quantidade or 0)
                    venda_produto[j][4] = int(vendaproduto.quantidade or 0)
                    j = j + 1
                    k = j - 1
                    codigo = vendaproduto.produto.codigo
                else:
                    # vou somando
                    venda_produto[k][2] += float(vendaproduto.preco_venda or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[k][3] += float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0) * float(
                        vendaproduto.quantidade or 0)
                    venda_produto[k][4] += vendaproduto.quantidade

            for vp in reversed(venda_produto):
                if vp[0] == 0:
                    venda_produto.remove(vp)

            # vendadiaria
            dt = periodo_retorno.ate - periodo_retorno.de
            venda_grafico = [[0 for i in xrange(4)] for i in xrange(dt.days + 1)]
            venda_grafico_dia = [0 for i in xrange(dt.days + 1)]
            venda_grafico_valor = [0 for i in xrange(dt.days + 1)]
            j = 0
            inicio = periodo_retorno.de
            while inicio <= periodo_retorno.ate:
                vendadiaria_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca,
                                                           dtrealizado=inicio)
                venda_grafico[j][0] = inicio
                venda_grafico_dia[j] = inicio
                k = 1
                for vendadiaria in vendadiaria_list:
                    venda_grafico_valor[j] += float(vendadiaria.preco_venda or 0) * float(vendadiaria.quantidade or 0)
                    venda_grafico[j][1] += float(vendadiaria.preco_venda or 0) * float(vendadiaria.quantidade or 0)
                    venda_grafico[j][2] = k
                    venda_grafico[j][3] += float(vendadiaria.quantidade or 0)
                    k = k + 1
                j = j + 1
                inicio += datetime.timedelta(days=1)

    saldo_cubagem_estoque = "%.2f" % round(saldo_cubagem_estoque, 2)
    saldo_cubagem_contratada_periodo = "%.2f" % round(saldo_cubagem_contratada_periodo, 2)
    return render(request, 'dashboard_marca.html',
                  {
                      'marca': marca,
                      'total_venda': total_venda,
                      'total_venda_periodo': total_venda_periodo,
                      'produtos_em_estoque': produtos_em_estoque,
                      'total_a_receber_periodo': total_a_receber_periodo,
                      'venda_valor_grafico': venda_valor_grafico,
                      'saldo_cubagem_contratada_periodo': saldo_cubagem_contratada_periodo,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'venda': venda,
                      'quantidade_produtos_checkin': quantidade_produtos_checkin,
                      'quantidade_produtos_devolvidos': quantidade_produtos_devolvidos,

                      'unidade_list': unidade_list,
                      'unidade_retorno': unidade_retorno,
                      'periodo_list': periodo_list,
                      'periodo_retorno': periodo_retorno,
                      'venda_list': venda_list,
                      'total_pecas_vendidas': total_pecas_vendidas,
                      'data_ultima_venda': data_ultima_venda,
                      'contrato': contrato,
                      'total_vendas': total_vendas,
                      'total_a_receber': total_a_receber,
                      'venda_grafico': venda_grafico,
                      'venda_grafico_dia': venda_grafico_dia,
                      'venda_grafico_valor': venda_grafico_valor,
                      'venda_produto': venda_produto,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def dashboard_operacional(request):
    return render(request, 'dashboard_operacional.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def lista_checkin_operacional(request):
    checkin_list = Checkin.objects.all().exclude(status='emprocessamento').order_by('-dia_agendamento')
    return render(request, 'lista_checkin_operacional.html', {'checkin_list': checkin_list})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def edita_checkin_operacional(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    miniloja_list = Miniloja.objects.filter(contrato__marca=checkin.marca)
    canal_list = Canal.objects.all()

    expedicao = Expedicao()
    produto = Produto()
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = Expedicao.objects.filter(checkin=checkin)
    contrato = None
    contrato_list = Contrato.objects.filter(marca=checkin.marca, miniloja__unidade=checkin.unidade)
    if contrato_list.count() != 0:
        contrato = contrato_list[0]

    if request.method == 'POST':
        # todo tratar erro, caso operador nao selecione status do produto
        # por enquanto, ta gravando ate o option=status... no bd em vez de dar um alerta.
        checkin.status = request.POST['statuscheckin']
        for expedicao in expedicao_list:
            expedicao.status = request.POST['status_produto_' + str(expedicao.produto.id)]

            if checkin.status == 'confirmado' and expedicao.status == 'ok':
                produto = Produto.objects.get(id=expedicao.produto.id)
                try:
                    estoque = Estoque.objects.get(produto=produto, unidade=checkin.unidade)
                    estoque.quantidade = estoque.quantidade + expedicao.quantidade
                    estoque.save()
                except Estoque.DoesNotExist:
                    estoque = Estoque()
                    estoque.produto = produto
                    estoque.unidade = checkin.unidade
                    estoque.quantidade = expedicao.quantidade
                    estoque.save()
                expedicao.gravou_estoque = True
            else:
                if expedicao.gravou_estoque:
                    # testo se a expedicao do produto "gravou_estoque"
                    try:
                        estoque = Estoque.objects.get(produto=expedicao.produto, unidade=checkin.unidade)
                        estoque.quantidade -= expedicao.quantidade
                        estoque.save()
                        expedicao.gravou_estoque = False
                    except Estoque.DoesNotExist:
                        # tirar except ou deixar nulo
                        # msg = "nao existe estoque para produto e checkin"
                        expedicao.gravou_estoque = False

            expedicao.save()
        checkin.save()

    return render(request, 'checkin_operacional.html',
                  {
                      'marca': checkin.marca,
                      'checkin': checkin,
                      'miniloja_list': miniloja_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'contrato': contrato,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def lista_checkout(request):
    checkout_list = Checkout.objects.all().exclude(motivo='venda')
    return render(request, 'lista_checkout.html', {'checkout_list': checkout_list})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def checkout(request):
    checkout = Checkout()
    marca_list = Marca.objects.all()
    unidade_list = None
    produto_list = None
    marca_retorno = None
    unidade_retorno = None
    produto_retorno = None
    dtrealizado_retorno = None
    checkout.motivo = request.GET.get('motivo')
    error = False
    estoque = None

    if request.method == 'POST':
        checkout.motivo = request.POST['motivo']
        checkout.observacao = request.POST['observacao']
        checkout.marca = Marca.objects.get(id=request.POST['marca'])
        checkout.unidade = Unidade.objects.get(id=request.POST['unidade'])
        checkout.produto = Produto.objects.get(id=request.POST['produtox'])

        if request.POST['dtrealizado'] != '':
            checkout.dtrealizado = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
            periodo_list = Periodo.objects.filter(ate__gte=checkout.dtrealizado,
                                                  de__lte=checkout.dtrealizado)  # é invertido mesmo. Poderia ser um get, mas se houver dois, não quero erro.
            for periodo in periodo_list:
                checkout.periodo = periodo
        estoque = Estoque.objects.get(unidade=checkout.unidade, produto=checkout.produto)
        checkout.quantidade = int(request.POST['quantidade'])
        if estoque.quantidade < checkout.quantidade:
            marca_retorno = checkout.marca
            unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca_retorno).distinct()
            unidade_retorno = checkout.unidade
            produto_list = marca_retorno.produto_set.filter(unidade=unidade_retorno)
            produto_retorno = checkout.produto

            error = True

        else:
            estoque.quantidade = estoque.quantidade - checkout.quantidade
            estoque.save()
            checkout.save()
            return HttpResponseRedirect(reverse('lista_checkout'))
    else:
        if "marca" in request.GET and request.GET['marca'] != '':
            marca_retorno = Marca.objects.get(id=request.GET['marca'])
            unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca_retorno).distinct()
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET[
            'unidade'] != '':
            unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])
            produto_list = marca_retorno.produto_set.filter(unidade=unidade_retorno)
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET[
            'unidade'] != '' and "produto" in request.GET and request.GET['produto'] != '':
            produto_retorno = Produto.objects.get(id=request.GET['produto'])
        if "marca" in request.GET and request.GET['marca'] != '' and "dtrealizado" in request.GET and request.GET[
            'dtrealizado'] != '':
            dtrealizado_retorno = datetime.datetime.strptime(request.GET['dtrealizado'], '%d/%m/%Y')

    return render(request, 'checkout.html',
                  {
                      'marca_list': marca_list,
                      'unidade_list': unidade_list,
                      'produto_list': produto_list,
                      'marca_retorno': marca_retorno,
                      'unidade_retorno': unidade_retorno,
                      'produto_retorno': produto_retorno,
                      'dtrealizado_retorno': dtrealizado_retorno,
                      'checkout': checkout,
                      'error': error,
                      'estoque': estoque,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def estoque(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca).distinct()
    estoque = None
    unidade_retorno = None
    estoque_list = None
    cubagem_contratada = 0
    cubagem_empenhada = 0
    saldo_cubagem_estoque = 0

    if request.method == 'GET' and "unidade" in request.GET and request.GET['unidade'] != '':
        estoque_list = Estoque.objects.filter(unidade_id=request.GET['unidade'], produto__marca=marca)
        unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])
        cubagem_contratada = memoriacalculo.CubagemContratada(marca, unidade_retorno)
        cubagem_empenhada = memoriacalculo.CubagemEmpenhada(marca, unidade_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(marca, unidade_retorno)

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque - cubagem_empenhada

    return render(request, 'estoque.html',
                  {
                      'marca': marca,
                      'unidade_list': unidade_list,
                      'estoque_list': estoque_list,
                      'unidade_retorno': unidade_retorno,
                      'cubagem_contratada': cubagem_contratada,
                      'cubagem_empenhada': cubagem_empenhada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def estoque_operacional(request):
    marca = Marca.objects.get.all()
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca).distinct()
    estoque = None
    unidade_retorno = None
    estoque_list = None

    if request.method == 'GET' and "unidade" in request.GET and request.GET['unidade'] != '':
        estoque_list = Estoque.objects.filter(unidade_id=request.GET['unidade'], produto__marca=marca)
        unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])

    return render(request, 'estoque_operacional.html',
                  {
                      'marca': marca,
                      'unidade_list': unidade_list,
                      'estoque_list': estoque_list,
                      'unidade_retorno': unidade_retorno,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def acompanhar_vendas_operacional(request):
    unidade = Unidade.objects.all().order_by('nome')
    venda_list = Checkout.objects.filter(motivo='venda').order_by('-dtrealizado', '-id')
    unidade_retorno = None

    if request.method == 'POST':
        if "unidade" in request.POST:
            venda_list = Checkout.objects.filter(unidade=request.POST['unidade']).order_by('-dtrealizado')
            unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])

    return render(request, 'operacional_acompanhar_venda.html', {
        'venda_list': venda_list,
        'unidade': unidade,
        'unidade_retorno': unidade_retorno
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def recomendar_marca(request):
    if request.method == 'POST':
        form = RecomendacaoForm(request.POST)
        if form.is_valid():
            marca = Marca.objects.get(user=request.user)
            recomendacao = form.save()
            recomendacao.marca = marca
            recomendacao.save()
            marca_recomendada = True
            return HttpResponseRedirect(reverse('recomendar_marca'), {
                'marca_recomendada': marca_recomendada
            })
        else:
            raise forms.ValidationError("Ha campos obrigatrios nao preenchidos")
    else:
        form = RecomendacaoForm()
    return render(request, 'recomendar_marca.html', {'form': form, 'error': False})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def acompanhar_venda(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca).distinct()
    unidade_retorno = None
    periodo_list = None
    periodo_retorno = None
    venda_list = None
    contrato = None
    data_ultima_venda = datetime.date(2000, 01, 01)
    total_pecas_vendidas = 0
    total_vendas = 0.0
    total_a_receber = 0.0
    venda_grafico = [[]]
    venda_produto = [[]]
    venda_grafico_dia = []
    venda_grafico_valor = []
    pagamento_de = datetime.date(2000, 01, 01)
    pagamento_ate = datetime.date(2000, 01, 01)
    if len(request.POST) != 0:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
        if "periodo" in request.POST and request.POST['periodo'] != '':
            periodo_retorno = Periodo.objects.get(id=request.POST['periodo'])
            pagamento_de = periodo_retorno.pagamento_de
            pagamento_ate = periodo_retorno.pagamento_ate


        contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=unidade_retorno)
        # primeiro contrato da lista
        if contrato_list.count() != 0:
            contrato = contrato_list[0]
            periodo_list = Periodo.objects.filter(contrato=contrato)
        else:
            contrato = None

        if periodo_retorno != None:

            venda_list = ItemVenda.objects.filter(checkout__status='confirmado', checkout__unidade=unidade_retorno,
                                                  produto__marca=marca,
                                                  checkout__dtrealizado__range=[periodo_retorno.de,
                                                                                periodo_retorno.ate])
            if venda_list.count() != 0:
                data_ultima_venda = datetime.date(2000, 01, 01)
                for venda in venda_list:
                    if venda.checkout.dtrealizado > data_ultima_venda:
                        data_ultima_venda = venda.checkout.dtrealizado
                    total_pecas_vendidas += venda.quantidade
                    total_vendas += float(venda.quantidade or 0) * float(venda.preco_venda or 0)
                    total_a_receber += float(memoriacalculo.PrecoReceber(venda, contrato) or 0) * float(
                        venda.quantidade or 0)

            # vendaPorProduto
            codigo = ''
            vendaproduto_list = ItemVenda.objects.filter(checkout__status='confirmado',
                                                         checkout__unidade=unidade_retorno, produto__marca=marca,
                                                         checkout__dtrealizado__range=[periodo_retorno.de,
                                                                                       periodo_retorno.ate]).order_by(
                'produto__codigo')
            # vendaproduto_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca, dtrealizado__range=[periodo_retorno.de, periodo_retorno.ate]).order_by('produto__codigo')
            # vou precisar limpar
            venda_produto = [[0 for i in xrange(5)] for i in xrange(vendaproduto_list.count())]
            j = 0
            for vendaproduto in vendaproduto_list:
                if codigo != vendaproduto.produto.codigo:
                    # zero as variaveis
                    venda_produto[j][0] = vendaproduto.produto.codigo
                    venda_produto[j][1] = vendaproduto.produto.nome
                    venda_produto[j][2] = float(vendaproduto.preco_venda or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[j][3] = float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0) * float(
                        vendaproduto.quantidade or 0)
                    venda_produto[j][4] = int(vendaproduto.quantidade or 0)
                    j = j + 1
                    k = j - 1
                    codigo = vendaproduto.produto.codigo
                else:
                    # vou somando
                    venda_produto[k][2] += float(vendaproduto.preco_venda or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[k][3] += float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0) * float(
                        vendaproduto.quantidade or 0)
                    venda_produto[k][4] += vendaproduto.quantidade

            for vp in reversed(venda_produto):
                if vp[0] == 0:
                    venda_produto.remove(vp)

            # vendadiaria
            dt = periodo_retorno.ate - periodo_retorno.de
            venda_grafico = [[0 for i in xrange(4)] for i in xrange(dt.days + 1)]
            venda_grafico_dia = [0 for i in xrange(dt.days + 1)]
            venda_grafico_valor = [0 for i in xrange(dt.days + 1)]
            j = 0
            inicio = periodo_retorno.de
            while inicio <= periodo_retorno.ate:
                vendadiaria_list = ItemVenda.objects.filter(checkout__status='confirmado',
                                                            checkout__unidade=unidade_retorno, produto__marca=marca,
                                                            checkout__dtrealizado=inicio)
                venda_grafico[j][0] = inicio
                venda_grafico_dia[j] = inicio
                k = 1
                for vendadiaria in vendadiaria_list:
                    venda_grafico_valor[j] += float(vendadiaria.preco_venda or 0) * float(vendadiaria.quantidade or 0)
                    venda_grafico[j][1] += float(vendadiaria.preco_venda or 0) * float(vendadiaria.quantidade or 0)
                    venda_grafico[j][2] = k
                    venda_grafico[j][3] += float(vendadiaria.quantidade or 0)
                    k = k + 1
                j = j + 1
                inicio += datetime.timedelta(days=1)

    # consequencia da falta de null date
    # todo nulldate
    if pagamento_de == datetime.date(2000, 01, 01):
        pagamento_de = ''
    if pagamento_ate == datetime.date(2000, 01, 01):
        pagamento_ate = ''

    return render(request, 'marca_acompanhar_venda.html',
                  {
                      'marca': marca,
                      'unidade_list': unidade_list,
                      'unidade_retorno': unidade_retorno,
                      'periodo_list': periodo_list,
                      'periodo_retorno': periodo_retorno,
                      'venda_list': venda_list,
                      'total_pecas_vendidas': total_pecas_vendidas,
                      'data_ultima_venda': data_ultima_venda,
                      'contrato': contrato,
                      'total_vendas': total_vendas,
                      'total_a_receber': total_a_receber,
                      'venda_grafico': venda_grafico,
                      'venda_grafico_dia': venda_grafico_dia,
                      'venda_grafico_valor': venda_grafico_valor,
                      'venda_produto': venda_produto,
                      'pagamento_de': pagamento_de,
                      'pagamento_ate': pagamento_ate,
                  }
                  )


# funções inicia_realizar_venda, edita_realizar_venda e estoque
# adicionar produto
def realizar_venda_adicionar_produto(lcheckout, lrequest, lestoque_retorno):
    error = ''
    if "quantidade" in lrequest.POST and int(lrequest.POST['quantidade'] or 0) <= 0:
        error = "Não se pode incluir quantidade menor ou igual a zero."

    if not error:
        lcheckout.quantidade = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        if "formapagamento" in lrequest.POST and lrequest.POST['formapagamento'] != '':
            lcheckout.formapagamento = lrequest.POST['formapagamento']
        lcheckout.preco_venda = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        lcheckout.save()
        itemvenda_list = ItemVenda.objects.filter(checkout=lcheckout, produto=lestoque_retorno.produto)
        for _ in itemvenda_list:
            error = 'Produto já existe neste checkout. Você deve excluí-lo antes de alterar a quantidade.'
        if error == '':
            itemvenda = ItemVenda()
            itemvenda.checkout = lcheckout
            itemvenda.produto = lestoque_retorno.produto
            itemvenda.preco_venda = lestoque_retorno.produto.preco_venda
            if "quantidade" in lrequest.POST and lrequest.POST['quantidade'] != '':
                itemvenda.quantidade = int(lrequest.POST['quantidade'])
            else:
                itemvenda.quantidade = 0
            itemvenda.save()

        lcheckout.quantidade = memoriacalculo.CalculoQuantidadeCheckout(lcheckout)
        lcheckout.preco_venda = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        lcheckout.save()

    return error


# funções inicia_realizar_venda e edita_realizar_venda e estoque
# remover produto
def realizar_venda_remover_produto(lcheckout, lrequest, lestoque_retorno):
    error = ''

    if "quantidade" in lrequest.POST and int(lrequest.POST['quantidade'] or 0) <= 0:
        error = "Não se pode excluir quantidade menor ou igual a zero."

    if not error:
        lcheckout.quantidade = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        if "formapagamento" in lrequest.POST and lrequest.POST['formapagamento'] != '':
            lcheckout.formapagamento = lrequest.POST['formapagamento']
        if "quantidade" in lrequest.POST and lrequest.POST['quantidade'] != '':
            quantidade = int(lrequest.POST['quantidade'])
        lcheckout.preco_venda = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        lcheckout.save()
        itemvenda_list = ItemVenda.objects.filter(checkout=lcheckout, produto=lestoque_retorno.produto)
        if itemvenda_list:
            for itemvenda in itemvenda_list:
                if itemvenda.quantidade == quantidade:
                    itemvenda.delete()
                if itemvenda.quantidade > quantidade:
                    itemvenda.quantidade -= quantidade
                    itemvenda.save()
                if itemvenda.quantidade < quantidade:
                    error = 'Não é possível excluir quantidade maior à do checkout.'
        else:
            error = 'Produto já não faz parte deste checkout.'

        lcheckout.quantidade = memoriacalculo.CalculoQuantidadeCheckout(lcheckout)
        lcheckout.preco_venda = memoriacalculo.CalculoPrecoVendaCheckout(lcheckout)
        lcheckout.save()
    return error


# funções inicia_realizar_venda e edita_realizar_venda e estoque
# atualizar estoque
@transaction.atomic
def realizar_venda_atualizar_estoque(lcheckout):
    try:
        with transaction.atomic():
            itemvenda_list = ItemVenda.objects.filter(checkout=lcheckout, gravou_estoque=0)
            for itemvenda in itemvenda_list:
                estoque_list = Estoque.objects.filter(produto=itemvenda.produto, unidade=lcheckout.unidade)
                if estoque_list:
                    for estoque in estoque_list:
                        if estoque.quantidade >= itemvenda.quantidade:
                            estoque.quantidade -= itemvenda.quantidade
                            estoque.save()
                            itemvenda.gravou_estoque = 1
                            itemvenda.save()
                        elif estoque.quantidade == itemvenda.quantidade:
                            estoque.quantidade.delete()
                            itemvenda.gravou_estoque = 1
                            itemvenda.save()
                        else:
                            erro = 'Quantidade de venda do produto ' + str(
                                itemvenda.produto.nome.encode('utf8')) + ' superior à quantidade presente no estoque. Quantidade em estoque: ' + str(
                                estoque.quantidade) + '.'
                            raise Exception(erro)
                else:
                    erro = 'Não há mais o produto ' + str(itemvenda.produto.nome.encode('utf8')) + ' no estoque para a unidade ' + str(
                        lcheckout.unidade.nome.encode('utf8')) + '.'
                    raise Exception(erro)
    except Exception as e:
        return e


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def inicia_realizar_venda(request):
    checkout = Checkout()
    canal_list = Canal.objects.all()
    unidade_list = None
    estoque_list = None
    unidade_retorno = None
    dtrealizado_retorno = None
    canal_retorno = None
    cliente_retorno = None
    estoque_retorno = None
    formapagamento_retorno = None
    itemvenda_list = None
    checkout.motivo = 'venda'
    error = False
    estoque = None
    preco_venda = None
    observacao_retorno = None
    unidade_list = Unidade.objects.all().distinct()

    if request.method == 'POST':
        if "observacao" in request.POST and request.POST['observacao'] != '':
            checkout.observacao = request.POST['observacao']
        if "unidade" in request.POST and request.POST['unidade'] != '':
            checkout.unidade = Unidade.objects.get(id=request.POST['unidade'])
        if "dtrealizado" in request.POST and request.POST['dtrealizado'] != '':
            checkout.dtrealizado = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
            periodo_list = Periodo.objects.filter(ate__gte=checkout.dtrealizado,
                                                  de__lte=checkout.dtrealizado)  # é invertido mesmo. Poderia ser um get, mas se houver dois, não quero erro.
            for periodo in periodo_list:
                checkout.periodo = periodo
        if "canal" in request.POST and request.POST['canal'] != '':
            checkout.canal = Canal.objects.get(id=request.POST['canal'])
        if "estoque" in request.POST and request.POST['estoque'] != '':
            produto = Produto.objects.get(id=request.POST['produtox'])
            estoque_list = Estoque.objects.get(produto_id=produto.id, unidade_id=checkout.unidade)
        if "telefone" in request.POST and request.POST['telefone'] != '':
            cliente_list = Cliente.objects.filter(telefone=request.POST['telefone'])

            for cliente in cliente_list:
                cliente_unidade_list = Cliente_Unidade.objects.filter(cliente=cliente, unidade=checkout.unidade)
                for cliente_unidade in cliente_unidade_list:
                    checkout.cliente_unidade_id = cliente_unidade.id
                if not cliente_unidade_list:
                    cliente_unidade = Cliente_Unidade()
                    cliente_unidade.cliente = cliente
                    cliente_unidade.unidade = checkout.unidade
                    cliente_unidade.save()
                    checkout.cliente_unidade = cliente_unidade

        if "observacao" in request.POST and request.POST['observacao'] != '':
            checkout.observacao = request.POST['observacao']
        if "formapagamento" in request.POST and request.POST['formapagamento'] != '':
            checkout.formapagamento = request.POST['formapagamento']

        # tratamento para Cliente
        if "telefone" in request.POST and request.POST['telefone'] != '':
            cliente_retorno_list = Cliente.objects.filter(telefone=request.POST['telefone'])
            for cliente_retorno in cliente_retorno_list:
                if "clientenome" in request.POST and request.POST['clientenome'] != '':
                    cliente_retorno.nome = request.POST['clientenome']
                if "clienteaniversario" in request.POST and request.POST['clienteaniversario'] != '':
                    cliente_retorno.aniversario = datetime.datetime.strptime(request.POST['clienteaniversario'],
                                                                             '%d/%m/%Y')

            if not cliente_retorno_list:
                cliente_retorno = Cliente()
                cliente_retorno.telefone = request.POST['telefone']
                if "clientenome" in request.POST and request.POST['clientenome'] != '':
                    cliente_retorno.nome = request.POST['clientenome']
                else:
                    cliente_retorno.nome = 'nome em processamento'
                if "clienteaniversario" in request.POST and request.POST['clienteaniversario'] != '':
                    cliente_retorno.aniversario = datetime.datetime.strptime(request.POST['clienteaniversario'],
                                                                             '%d/%m/%Y')
            cliente_retorno.save()

        if "canal" in request.POST and request.POST['canal'] != '':
            canal_retorno = Canal.objects.get(id=request.POST['canal'])
        if "dtrealizado" in request.POST and request.POST['dtrealizado'] != '':
            dtrealizado_retorno = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
        if "observacao" in request.POST and request.POST['observacao'] != '':
            observacao_retorno = request.POST['observacao']
        if "unidade" in request.POST and request.POST['unidade'] != '':
            unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
            estoque_list = Estoque.objects.filter(unidade=unidade_retorno)
        if "unidade" in request.POST and request.POST['unidade'] != '' and "produto" in request.POST and request.POST[
            'produto'] != '':
            estoque_retorno = Estoque.objects.get(produto_id=request.POST['estoque'])
            preco_venda = estoque_retorno.produto.preco_venda
        if "estoque" in request.POST and request.POST['estoque'] != '':
            produto = Produto.objects.get(id=request.POST['produtox'])
            estoque_retorno = Estoque.objects.get(produto_id=produto.id, unidade_id=checkout.unidade)
            preco_venda = estoque_retorno.produto.preco_venda
        if "formapagamento" in request.POST and request.POST['formapagamento'] != '':
            formapagamento_retorno = request.POST['formapagamento']

    if "adicionar_produto" in request.POST:
        error = realizar_venda_adicionar_produto(checkout, request, estoque_retorno)
        if not error:
            return HttpResponseRedirect('/operacional/realizar-venda/' + str(checkout.id))

    if "remover_produto" in request.POST:
        error = realizar_venda_remover_produto(checkout, request, estoque_retorno)
        if not error:
            return HttpResponseRedirect('/operacional/realizar-venda/' + str(checkout.id))

    if "finalizar" in request.POST:
        error = 'Favor inserir produtos.'

    preco_calculado = memoriacalculo.CalculoPrecoVendaCheckout(checkout)

    return render(request, 'realizar_venda.html',
                  {
                      'unidade_list': unidade_list,
                      'estoque_list': estoque_list,
                      'itemvenda_list': itemvenda_list,
                      'unidade_retorno': unidade_retorno,
                      'estoque_retorno': estoque_retorno,
                      'dtrealizado_retorno': dtrealizado_retorno,
                      'checkout': checkout,
                      'error': error,
                      'canal_list': canal_list,
                      'canal_retorno': canal_retorno,
                      'preco_venda': preco_venda,
                      'preco_calculado': preco_calculado,
                      'cliente_retorno': cliente_retorno,
                      'observacao_retorno': observacao_retorno,
                      'formapagamento_retorno': formapagamento_retorno,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def edita_realizar_venda(request, id):
    checkout = get_object_or_404(Checkout, id=id)
    canal_list = Canal.objects.all()
    unidade_list = Unidade.objects.all().distinct()
    unidade_retorno = checkout.unidade
    dtrealizado_retorno = checkout.dtrealizado
    canal_retorno = checkout.canal
    if checkout.cliente_unidade:
        cliente_retorno = checkout.cliente_unidade.cliente
    else:
        cliente_retorno = None
    estoque_retorno = None
    formapagamento_retorno = checkout.formapagamento
    checkout.motivo = 'venda'
    error = False
    preco_venda = None
    observacao_retorno = checkout.observacao
    unidade_list = Unidade.objects.all().distinct()
    itemvenda_list = ItemVenda.objects.filter(checkout=checkout)
    estoque_list = Estoque.objects.filter(unidade=checkout.unidade)

    if request.method == 'POST':
        if "observacao" in request.POST and request.POST['observacao'] != '':
            checkout.observacao = request.POST['observacao']
        if "formapagamento" in request.POST and request.POST['formapagamento'] != '':
            checkout.formapagamento = request.POST['formapagamento']
        if "dtrealizado" in request.POST and request.POST['dtrealizado'] != '':
            checkout.dtrealizado = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
            periodo_list = Periodo.objects.filter(ate__gte=checkout.dtrealizado,
                                                  de__lte=checkout.dtrealizado)  # é invertido mesmo. Poderia ser um get, mas se houver dois, não quero erro.
            for periodo in periodo_list:
                checkout.periodo = periodo
        if "canal" in request.POST and request.POST['canal'] != '':
            checkout.canal = Canal.objects.get(id=request.POST['canal'])
        if "telefone" in request.POST and request.POST['telefone'] != '':
            cliente_list = Cliente.objects.filter(telefone=request.POST['telefone'])

            for cliente in cliente_list:
                cliente_unidade_list = Cliente_Unidade.objects.filter(cliente=cliente, unidade=checkout.unidade)
                for cliente_unidade in cliente_unidade_list:
                    checkout.cliente_unidade_id = cliente_unidade.id
                if not cliente_unidade_list:
                    cliente_unidade = Cliente_Unidade()
                    cliente_unidade.cliente = cliente
                    cliente_unidade.unidade = checkout.unidade
                    cliente_unidade.save()
                    checkout.cliente_unidade = cliente_unidade

        if "observacao" in request.POST and request.POST['observacao'] != '':
            checkout.observacao = request.POST['observacao']

        # tratamento para Cliente
        if "telefone" in request.POST and request.POST['telefone'] != '':
            cliente_retorno_list = Cliente.objects.filter(telefone=request.POST['telefone'])
            for cliente_retorno in cliente_retorno_list:
                if "clientenome" in request.POST and request.POST['clientenome'] != '':
                    cliente_retorno.nome = request.POST['clientenome']
                if "clienteaniversario" in request.POST and request.POST['clienteaniversario'] != '':
                    cliente_retorno.aniversario = datetime.datetime.strptime(request.POST['clienteaniversario'],
                                                                             '%d/%m/%Y')

            if not cliente_retorno_list:
                cliente_retorno = Cliente()
                cliente_retorno.telefone = request.POST['telefone']
                if "clientenome" in request.POST and request.POST['clientenome'] != '':
                    cliente_retorno.nome = request.POST['clientenome']
                else:
                    cliente_retorno.nome = 'nome em processamento'
                if "clienteaniversario" in request.POST and request.POST['clienteaniversario'] != '':
                    cliente_retorno.aniversario = datetime.datetime.strptime(request.POST['clienteaniversario'],
                                                                             '%d/%m/%Y')
            cliente_retorno.save()

        if "canal" in request.POST and request.POST['canal'] != '':
            canal_retorno = Canal.objects.get(id=request.POST['canal'])
        if "dtrealizado" in request.POST and request.POST['dtrealizado'] != '':
            dtrealizado_retorno = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
        if "observacao" in request.POST and request.POST['observacao'] != '':
            observacao_retorno = request.POST['observacao']
        if "unidade" in request.POST and request.POST['unidade'] != '':
            unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
            estoque_list = Estoque.objects.filter(unidade=checkout.unidade)
        if "unidade" in request.POST and request.POST['unidade'] != '' and "produto" in request.POST and request.POST[
            'produto'] != '':
            estoque_retorno = Estoque.objects.get(produto_id=request.POST['estoque'])
            preco_venda = estoque_retorno.produto.preco_venda
        if "estoque" in request.POST and request.POST['estoque'] != '':
            produtonome = Produto.objects.get(nome=request.POST['estoque'])
            estoque_retorno = Estoque.objects.get(produto_id=produtonome.id, unidade_id=checkout.unidade)
            preco_venda = estoque_retorno.produto.preco_venda
        if "formapagamento" in request.POST and request.POST['formapagamento'] != '':
            formapagamento_retorno = request.POST['formapagamento']

    if "adicionar_produto" in request.POST:
        error = realizar_venda_adicionar_produto(checkout, request, estoque_retorno)

    if "remover_produto" in request.POST:
        error = realizar_venda_remover_produto(checkout, request, estoque_retorno)

    if "finalizar" in request.POST:
        error = realizar_venda_atualizar_estoque(checkout)
        if not error:
            if request.POST.get('formapagamento') == None:
                error = "A forma de pagamento deve ser informada."
            if "unidade" in request.POST and request.POST['unidade'] == '':
                error = "A unidade de venda deve ser informada."
            if "dtrealizado" in request.POST and request.POST['dtrealizado'] == '':
                error = "A data de venda deve ser informada."
            if "canal" in request.POST and request.POST['canal'] == '':
                error = "O canal deve ser informado."
            # if "telefone" in request.POST and request.POST['telefone'] == '':
            #     error = "O número do telefone do cliente deve ser informado."
            # if "clientenome" in request.POST and request.POST['clientenome'] == '':
            #     error = "O nome do cliente deve ser informado."
            if not itemvenda_list:
                error = "Favor inserir produtos."
            if not error:
                checkout.status = 'confirmado'
                checkout.save()
                return HttpResponseRedirect('/operacional/realizar-venda/')

    preco_calculado = memoriacalculo.CalculoPrecoVendaCheckout(checkout)
    return render(request, 'realizar_venda.html',
                  {
                      'unidade_list': unidade_list,
                      'estoque_list': estoque_list,
                      'itemvenda_list': itemvenda_list,
                      'unidade_retorno': unidade_retorno,
                      'estoque_retorno': estoque_retorno,
                      'dtrealizado_retorno': dtrealizado_retorno,
                      'checkout': checkout,
                      'error': error,
                      'canal_list': canal_list,
                      'canal_retorno': canal_retorno,
                      'preco_venda': preco_venda,
                      'preco_calculado': preco_calculado,
                      'cliente_retorno': cliente_retorno,
                      'observacao_retorno': observacao_retorno,
                      'formapagamento_retorno': formapagamento_retorno,
                  }
                  )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
@transaction.atomic
def importacao(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    erro = ''

    if request.method == 'POST':
        form = ImportacaoForm(request.POST, request.FILES)
        if form.is_valid():
            importacao = Importacao()
            importacao.dia = datetime.datetime.now().strftime('%Y-%m-%d')
            importacao.hora = datetime.datetime.now().strftime('%H:%M:%S')
            importacao.marca = marca
            importacao.status = 'recebido'
    else:
        form = ImportacaoForm()
        return render(request, 'importacao.html', {'form': form})

    try:
        with transaction.atomic():
            for filename, file in request.FILES.iteritems():
                xl_workbook = xlrd.open_workbook(file_contents=file.read())
                sheet_names = xl_workbook.sheet_names()
                importacao.arquivo.save(file.name, File(file))
                xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
                xl_sheet = xl_workbook.sheet_by_index(0)
                row = xl_sheet.row(0)  # 1st row
                from xlrd.sheet import ctype_text
                for idx, cell_obj in enumerate(row):
                    cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
                num_cols = xl_sheet.ncols  # Number of columns
                for row_idx in range(0, xl_sheet.nrows - 1):  # Iterate through rows
                    print ('-' * 40)
                    print ('Row: %s' % str(row_idx + 1))  # Print row number
                    # try:
                    produto = Produto()
                    produto.codigo = marca.codigo.strip() + str(int(marca.sequencial_atual or 0) + 1).zfill(
                        4)
                    produto.marca = marca
                    produto.codigo_marca = xl_sheet.cell(row_idx + 1, 0).value.encode('utf8')
                    produto.nome = xl_sheet.cell(row_idx + 1, 1).value.encode('utf8')
                    produto.descricao = xl_sheet.cell(row_idx + 1, 2).value.encode('utf8')
                    produto.unidade_venda = xl_sheet.cell(row_idx + 1, 3).value.lower().encode('utf8')
                    produto.preco_venda = float(xl_sheet.cell(row_idx + 1, 4).value or 0)
                    produto.estoque_minimo = int(xl_sheet.cell(row_idx + 1, 5).value or 0)
                    produto.ncm = str(str(xl_sheet.cell(row_idx + 1, 6).value).encode('utf8') or '')
                    produto.altura = float(xl_sheet.cell(row_idx + 1, 7).value or 0)
                    produto.largura = float(xl_sheet.cell(row_idx + 1, 8).value or 0)
                    produto.profundidade = float(xl_sheet.cell(row_idx + 1, 9).value or 0)
                    produto.peso = float(xl_sheet.cell(row_idx + 1, 10).value or 0)
                    produto.itens_inclusos = str(xl_sheet.cell(row_idx + 1, 11).value.encode('utf8') or '')
                    produto.garantia = int(xl_sheet.cell(row_idx + 1, 12).value or 0)
                    produto.palavras_chaves = str(xl_sheet.cell(row_idx + 1, 13).value.encode('utf8') or '')
                    emestoque = xl_sheet.cell(row_idx + 1, 14).value.encode('utf8')
                    if emestoque.encode('utf-8').lower() == 'sim':
                        produto.em_estoque = 'sim'
                    elif emestoque.encode('utf-8').lower() == 'nao':
                        produto.em_estoque = 'nao'
                    elif emestoque.encode('utf-8').lower() == 'não':
                        produto.em_estoque = 'nao'
                    else:
                        raise Exception('. Posição em-estoque não informada.')
                    produto.status = str(xl_sheet.cell(row_idx + 1, 15).value.encode('utf8') or '')
                    produto.save()
                    marca.sequencial_atual = int(marca.sequencial_atual) + 1
                    marca.save()
    except Exception as e:
        importacao.status = 'erronoarquivo'
        importacao.save()
        return HttpResponse('Importação não realizada. Linha:' + str(row_idx + 2) + str(e))

    importacao.status = 'importadocomsucesso'
    importacao.save()
    return HttpResponse('Importação realizada com sucesso!')
