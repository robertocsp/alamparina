# -*- coding: utf-8 -*-

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
from django.template.context_processors import request
from django.utils import *

from administrativo.models import *
from models import Canal
from models import Produto
from models import Recomendacao
from operacional.forms import *

# Create your views here.
from alamparina.library import memoriacalculo
import datetime
import time

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')

#a ideia e fazer um login unico verificando se e marca ou operacao
def login_geral(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            #No caso abaixo se o username nao existir ele atribui valor vazio, este caso e mais valido para metodo GET
            #username = request.POST.get('username','')
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
    #produto_list = Produto.objects.filter(marca__id=marca.id)
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
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.marca = marca
            #jogar pra dentro do models
            #mas vou precisar salvar marca
            produto.codigo= marca.codigo.strip() + str(marca.sequencial_atual).zfill(4)
            produto.save()
            marca.sequencial_atual = int(marca.sequencial_atual) + 1
            marca.save()
            produto_cadastado = True
            return HttpResponseRedirect(reverse('marca_cadastra_produto'), {'produto_cadastrado':produto_cadastado})

    else:
        form = ProdutoForm()
    return render(request,'marca_cadastra_produto.html',{'form':form,'marca':marca})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def edita_produto(request,id):
    produto = get_object_or_404(Produto, id=id)
    marca = Marca.objects.get(id=request.session['marca_id'])
    if request.method == 'POST':
        form = ProdutoForm(request.     POST, instance=produto)
        if form.is_valid():
            #jogar pra dentro do models
            #mas vou precisar salvar marca
            produto.codigo= marca.codigo.strip() + str(marca.sequencial_atual).zfill(4)
            produto.save()
            marca.sequencial_atual = int(marca.sequencial_atual) + 1
            marca.save()
            return render(request,'marca_cadastra_produto.html',{'form':form,'marca':marca, 'produto_cadastrado':True})

    else:
        form = ProdutoForm(instance=produto)
    return render(request,'marca_cadastra_produto.html',{'form':form,'marca':marca})
    #return HttpResponseRedirect(reverse('marca_cadastra_produto'))

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def lista_checkin(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    checkin_list = Checkin.objects.filter(marca__id=marca.id)
    return render(request, 'lista_checkin.html', {'checkin_list': checkin_list, 'marca': marca})


#funções inicia_checkin e edita_checkin
def adicionar_canal(lcheckin, lrequest):
    lcheckin.dia_agendamento = datetime.datetime.strptime(lrequest.POST['dia_agendamento'], '%d/%m/%Y')
    lcheckin.save()
    lcheckin.canal.add(Canal.objects.get(id=lrequest.POST['canais']))

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def inicia_checkin(request):
    checkin = Checkin()
    checkin.tipo = 'chin'
    checkin.marca = Marca.objects.get(id=request.session['marca_id'])
    checkin.status = 'emprocessamento'
    cubagem_contratada = 0
    saldo_cubagem_estoque = 0
    expedicao_list = None
    contrato_list = None
    contrato = None
    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=checkin.marca).distinct()
    if len(request.POST) == 0 or request.POST['unidade'] == '':
        miniloja_list = None
        canal_list = None
        produto_list = None
        unidade_retorno = None
    else:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
        checkin.unidade_id = request.POST['unidade']
        miniloja_list = Miniloja.objects.filter(contrato__marca=checkin.marca, unidade_id=request.POST['unidade']).distinct()
        canal_list = Canal.objects.all()
        cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, unidade_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(checkin.marca, unidade_retorno)
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
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        checkin.save()
        expedicao.produto = produto
        expedicao.checkin = checkin
        expedicao.save()
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

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

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque

    return render(request,'checkin.html',
                  {
                      'marca': checkin.marca,
                      'checkin':checkin,
                      'miniloja_list':miniloja_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'cubagem_contratada': cubagem_contratada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                      'unidade_list': unidade_list,
                      'unidade_retorno': unidade_retorno,
                      'contrato': contrato,
                  }
    )

@login_required
@user_passes_test(lambda u: u.groups.filter(name='marca').count() != 0, login_url='/login')
def edita_checkin(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    expedicao = Expedicao()

    if len(request.POST) != 0:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
        checkin.unidade_id = request.POST['unidade']
    else:
        unidade_retorno = Unidade.objects.get(id=checkin.unidade_id)

    expedicao_list = Expedicao.objects.filter(checkin=checkin)

    unidade_list = Unidade.objects.filter(miniloja__contrato__marca=checkin.marca).distinct()
    canal_list = Canal.objects.all()
    contrato_list = Contrato.objects.filter(marca=checkin.marca, miniloja__unidade=unidade_retorno)
    if contrato_list.count() != 0:
      contrato = contrato_list[0]
    else:
      contrato = None

    cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, unidade_retorno)
    saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(checkin.marca, unidade_retorno)

    miniloja_list = Miniloja.objects.filter(contrato__marca=checkin.marca, unidade_id=checkin.unidade_id).distinct()
    produto_list = checkin.marca.produto_set.all()

    if "adicionar_canal" in request.POST:
        adicionar_canal(checkin, request)

    elif "remover_canal" in request.POST:
        checkin.canal.remove(Canal.objects.get(id=request.POST['canais']))
        checkin.save()

    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        expedicao.produto = produto
        expedicao.checkin = checkin
        checkin.save()
        expedicao.save()

    elif "remover_produto" in request.POST:

        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao_remove = Expedicao.objects.filter(checkin=checkin, produto=produto)
        if expedicao_remove: #ajeitar urgente esse expedicao_remove. Faço FILTER para testar para null, se for not null, faço um get.. :/
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
            messages.error(request, 'Não existe nenhum produto inserido')
        else:
            checkin.status = checkin.status_enviado()
            checkin.save()

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque

    return render(request, 'checkin.html',
                  {
                      'marca': checkin.marca,
                      'checkin': checkin,
                      'miniloja_list': miniloja_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'cubagem_contratada': cubagem_contratada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                      'unidade_list': unidade_list,
                      'unidade_retorno': unidade_retorno,
                      'contrato': contrato,
                  }
    )

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

    for venda in venda_list:
        total_venda += 1

    data_hoje = time.strftime("%Y-%m-%d")
    periodo_list = Periodo.objects.filter(ate__gte=data_hoje, de__lte=data_hoje) #é invertido mesmo.
    for periodo in periodo_list:
        periodo_atual = periodo
        vendaperiodo_list = Checkout.objects.filter(motivo='venda', marca=marca,
                                                    dtrealizado__range=[periodo.de, periodo.ate])
        for vendaperiodo in vendaperiodo_list:
            total_venda_periodo += 1
            #preciso obter o contrato da venda (row do queryset Checkout)
            contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=vendaperiodo.unidade)
            if contrato_list.count() != 0:
                contrato = contrato_list[0]
                total_a_receber_periodo += float(memoriacalculo.PrecoReceber(vendaperiodo, contrato) or 0)*(float(vendaperiodo.quantidade) or 0)
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
        vendaperiodo_list = Checkout.objects.filter(motivo='venda', marca=marca,
                                                    dtrealizado__range=[periodo.de, periodo.ate])
        preco_venda_periodo = 0
        for vendaperiodo in vendaperiodo_list:
           preco_venda_periodo += vendaperiodo.preco_venda
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

    ultimasvendas_list = Checkout.objects.filter(motivo='venda', marca=marca).order_by('-dtrealizado')
    venda = [[0 for i in xrange(5)] for i in xrange(6)]
    j = 0
    for ultimasvendas in ultimasvendas_list:
        venda[0][j] = ultimasvendas.produto.nome
        venda[1][j] = ultimasvendas.dtrealizado
        venda[2][j] = "%.2f" % round(ultimasvendas.preco_venda, 2)
        venda[3][j] = ultimasvendas.quantidade
        # todo o lance do contrato ta confuso.
        contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=ultimasvendas.unidade)
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
    return render (request, 'dashboard_operacional.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def lista_checkin_operacional(request):
    checkin_list = Checkin.objects.all().exclude(status='emprocessamento')
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
            expedicao.status = request.POST['status_produto_'+str(expedicao.produto.id)]

            if checkin.status == 'confirmado' and expedicao.status == 'ok':
                produto = Produto.objects.get(id=expedicao.produto.id)
                try:
                    estoque = Estoque.objects.get(produto=produto,unidade=checkin.unidade)
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
    checkout.motivo = request.GET.get('motivo')
    error = False
    estoque = None

    if request.method=='POST':
        checkout.motivo = request.POST['motivo']
        checkout.observacao = request.POST['observacao']
        checkout.marca = Marca.objects.get(id=request.POST['marca'])
        checkout.unidade = Unidade.objects.get(id=request.POST['unidade'])
        checkout.produto = Produto.objects.get(id=request.POST['produto'])
        estoque = Estoque.objects.get(unidade=checkout.unidade,produto=checkout.produto)
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
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET['unidade'] != '' :
            unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])
            produto_list = marca_retorno.produto_set.filter(unidade=unidade_retorno)
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET['unidade'] != '' and "produto" in request.GET and request.GET['produto'] != '':
            produto_retorno = Produto.objects.get(id=request.GET['produto'])


    return render(request,'checkout.html',
                 {
                     'marca_list':marca_list,
                     'unidade_list':unidade_list,
                     'produto_list':produto_list,
                     'marca_retorno':marca_retorno,
                     'unidade_retorno':unidade_retorno,
                     'produto_retorno':produto_retorno,
                     'checkout':checkout,
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
    saldo_cubagem_estoque = 0

    if request.method == 'GET' and "unidade" in request.GET and request.GET['unidade'] != '':
        estoque_list = Estoque.objects.filter(unidade_id=request.GET['unidade'], produto__marca=marca)
        unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])
        cubagem_contratada = memoriacalculo.CubagemContratada(marca, unidade_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueUnidade(marca, unidade_retorno)

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque

    return render(request, 'estoque.html',
                  {
                      'marca': marca,
                      'unidade_list': unidade_list,
                      'estoque_list': estoque_list,
                      'unidade_retorno': unidade_retorno,
                      'cubagem_contratada': cubagem_contratada,
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
    venda_list = Checkout.objects.filter(motivo='venda', unidade=unidade).order_by('-dtrealizado')
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
@user_passes_test(lambda u: u.groups.filter(name='operacional').count() != 0, login_url='/login')
def realizar_venda(request):
    checkout = Checkout()
    marca_list = Marca.objects.all()
    canal_list = Canal.objects.all()
    unidade_list = None
    produto_list = None
    marca_retorno = None
    unidade_retorno = None
    produto_retorno = None
    dtrealizado_retorno = None
    canal_retorno = None
    #checkout.motivo = request.GET.get('motivo')
    checkout.motivo = 'venda'
    error = False
    estoque = None
    preco_venda = None

    if request.method=='POST':
        checkout.observacao = request.POST['observacao']
        checkout.marca = Marca.objects.get(id=request.POST['marca'])
        checkout.unidade = Unidade.objects.get(id=request.POST['unidade'])
        checkout.produto = Produto.objects.get(id=request.POST['produto'])
        checkout.dtrealizado = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
        checkout.canal = Canal.objects.get(id=request.POST['canal'])
        checkout.preco_venda = checkout.produto.preco_venda
        estoque = Estoque.objects.get(unidade=checkout.unidade,produto=checkout.produto)
        checkout.quantidade = int(request.POST['quantidade'])
        preco_venda = checkout.produto.preco_venda
        if estoque.quantidade < checkout.quantidade:
            marca_retorno = checkout.marca
            unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca_retorno).distinct()
            unidade_retorno = checkout.unidade
            produto_list = marca_retorno.produto_set.filter(unidade=unidade_retorno)
            produto_retorno = checkout.produto
            canal_retorno = checkout.canal
            error = True

        else:
            estoque.quantidade = estoque.quantidade - checkout.quantidade
            estoque.save()
            checkout.save()
            return HttpResponseRedirect(reverse('realizar_venda'))
    else:
        if "canal" in request.GET and request.GET['canal'] != '':
            canal_retorno = Canal.objects.get(id=request.GET['canal'])
        if "dtrealizado" in request.GET and request.GET['dtrealizado'] != '':
            dtrealizado_retorno = request.GET['dtrealizado']
        if "marca" in request.GET and request.GET['marca'] != '':
            marca_retorno = Marca.objects.get(id=request.GET['marca'])
            unidade_list = Unidade.objects.filter(miniloja__contrato__marca=marca_retorno).distinct()
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET['unidade'] != '' :
            unidade_retorno = Unidade.objects.get(id=request.GET['unidade'])
            produto_list = marca_retorno.produto_set.filter(unidade=unidade_retorno)
        if "marca" in request.GET and request.GET['marca'] != '' and "unidade" in request.GET and request.GET['unidade'] != '' and "produto" in request.GET and request.GET['produto'] != '':
            produto_retorno = Produto.objects.get(id=request.GET['produto'])
            preco_venda = produto_retorno.preco_venda

    return render(request,'realizar_venda.html',
                 {
                     'marca_list':marca_list,
                     'unidade_list':unidade_list,
                     'produto_list':produto_list,
                     'marca_retorno':marca_retorno,
                     'unidade_retorno':unidade_retorno,
                     'produto_retorno':produto_retorno,
                     'dtrealizado_retorno':dtrealizado_retorno,
                     'checkout': checkout,
                     'error': error,
                     'estoque': estoque,
                     'canal_list': canal_list,
                     'canal_retorno': canal_retorno,
                     'preco_venda': preco_venda,
                  }
    )

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
    data_ultima_venda = datetime.date(2000,01,01)
    total_pecas_vendidas = 0
    total_vendas = 0.0
    total_a_receber = 0.0
    venda_grafico = [[]]
    venda_produto = [[]]
    venda_grafico_dia =[]
    venda_grafico_valor =[]
    pagamento_de = datetime.date(2000,01,01)
    pagamento_ate = datetime.date(2000,01,01)
    if len(request.POST) != 0:
        unidade_retorno = Unidade.objects.get(id=request.POST['unidade'])
        if "periodo" in request.POST and request.POST['periodo'] != '':
            periodo_retorno = Periodo.objects.get(id=request.POST['periodo'])
            pagamento_de = periodo_retorno.pagamento_de
            pagamento_ate = periodo_retorno.pagamento_ate
        # periodo
        periodo_list = Periodo.objects.all()
        # venda (groupby produto, sum(qtd))
        if periodo_retorno != None:
            contrato_list = Contrato.objects.filter(marca=marca, miniloja__unidade=unidade_retorno)
            if contrato_list.count() != 0:
                contrato = contrato_list[0]
            else:
                contrato = None
            venda_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca, dtrealizado__range=[periodo_retorno.de, periodo_retorno.ate])
            if venda_list.count() != 0:
                data_ultima_venda = datetime.date(2000,01,01)
                for venda in venda_list:
                    if venda.dtrealizado > data_ultima_venda:
                        data_ultima_venda = venda.dtrealizado
                    total_pecas_vendidas += venda.quantidade
                    total_vendas += float(venda.quantidade or 0)*float(venda.preco_venda or 0)
                    total_a_receber += float(memoriacalculo.PrecoReceber(venda, contrato) or 0)*float(venda.quantidade or 0)
            #vendaPorProduto
            codigo = ''
            vendaproduto_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca, dtrealizado__range=[periodo_retorno.de, periodo_retorno.ate]).order_by('produto__codigo')
            #vou precisar limpar
            venda_produto = [[0 for i in xrange(5)] for i in xrange(vendaproduto_list.count())]
            j = 0
            for vendaproduto in vendaproduto_list:
                if codigo != vendaproduto.produto.codigo:
                    #zero as variaveis
                    venda_produto[j][0] = vendaproduto.produto.codigo
                    venda_produto[j][1] = vendaproduto.produto.nome
                    venda_produto[j][2] = float(vendaproduto.preco_venda or 0)*float(vendaproduto.quantidade or 0)
                    venda_produto[j][3] = float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0)*float(vendaproduto.quantidade or 0)
                    venda_produto[j][4] = int(vendaproduto.quantidade or 0)
                    j = j + 1
                    k = j - 1
                    codigo = vendaproduto.produto.codigo
                else:
                    #vou somando
                    venda_produto[k][2] += float(vendaproduto.preco_venda or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[k][3] += float(memoriacalculo.PrecoReceber(vendaproduto, contrato) or 0) * float(vendaproduto.quantidade or 0)
                    venda_produto[k][4] += vendaproduto.quantidade

            for vp in reversed(venda_produto):
                if vp[0] == 0:
                    venda_produto.remove(vp)

            #vendadiaria
            dt = periodo_retorno.ate - periodo_retorno.de
            venda_grafico = [[0 for i in xrange(4)] for i in xrange(dt.days + 1)]
            venda_grafico_dia = [0 for i in xrange(dt.days + 1)]
            venda_grafico_valor = [0 for i in xrange(dt.days + 1)]
            j = 0
            inicio = periodo_retorno.de
            while inicio <= periodo_retorno.ate:
                vendadiaria_list = Checkout.objects.filter(motivo='venda', unidade=unidade_retorno, marca=marca, dtrealizado=inicio)
                venda_grafico[j][0] = inicio
                venda_grafico_dia[j] = inicio
                k = 1
                for vendadiaria in vendadiaria_list:
                    venda_grafico_valor[j] += float(vendadiaria.preco_venda or 0)*float(vendadiaria.quantidade or 0)
                    venda_grafico[j][1] += float(vendadiaria.preco_venda or 0)*float(vendadiaria.quantidade or 0)
                    venda_grafico[j][2] = k
                    venda_grafico[j][3] += float(vendadiaria.quantidade or 0)
                    k = k + 1
                j = j + 1
                inicio += datetime.timedelta(days=1)

    #consequencia da falta de null date
    # todo nulldate
    if pagamento_de == datetime.date(2000,01,01):
        pagamento_de = ''
    if pagamento_ate == datetime.date(2000,01,01):
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

