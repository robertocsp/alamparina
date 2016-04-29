# -*- coding: utf-8 -*-
from distutils.command.check import check
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, render_to_response

from administrativo.models import *
from models import Canal
from models import Produto
from models import Recomendacao
from operacional.forms import *

# Create your views here.
from alamparina.library import memoriacalculo
import datetime

#a ideia e fazer um login unico verificando se e marca ou operacao
def login_operacional(request):
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
                try:
                    marca = Marca.objects.get(user=request.user)
                    request.session['marca_id'] = marca.id
                    return HttpResponseRedirect('/marca/dashboard/')
                except:
                    return HttpResponseRedirect('/operacional/dashboard/')
            else:
                return render(request, 'login_marca.html', {'form': form, 'error': True})
        else:
            raise forms.ValidationError("Algum nome ou id incoerrente com o formulario")
    else:
        form = LoginForm()
        return render(request, 'login_marca.html', {'form': form, 'error': False})

@login_required
def lista_produtos(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    #produto_list = Produto.objects.filter(marca__id=marca.id)
    produto_list = marca.produto_set.all()
    return render(request, 'lista_produtos.html', {'produto_list': produto_list, 'marca': marca})

@login_required
def lista_produtos_operacional(request):
    marca = Marca.objects.get()
    produto_list = marca.produto_set.all()

    return render(request, 'lista_produtos_operacional.html', {
        'produto_list': produto_list,
        'marca': marca

    })

@login_required
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
def edita_produto(request,id):
    produto = get_object_or_404(Produto, id=id)
    marca = Marca.objects.get(id=request.session['marca_id'])
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            #jogar pra dentro do models
            #mas vou precisar salvar marca
            produto.codigo= marca.codigo.strip() + str(marca.sequencial_atual).zfill(4)
            produto.save()
            marca.sequencial_atual = int(marca.sequencial_atual) + 1
            marca.save()
            produto_cadastado = True
            return render(request,'marca_cadastra_produto.html',{'form':form,'marca':marca, 'produto_cadastrado':True})

    else:
        form = ProdutoForm(instance=produto)
    return render(request,'marca_cadastra_produto.html',{'form':form,'marca':marca})
    #return HttpResponseRedirect(reverse('marca_cadastra_produto'))

@login_required
def lista_checkin(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    checkin_list = Checkin.objects.filter(marca__id=marca.id)
    return render(request, 'lista_checkin.html', {'checkin_list': checkin_list, 'marca': marca})


#funções inicia_checkin e edita_checkin
def adicionar_canal(lcheckin, lrequest):
    lcheckin.dia_agendamento = datetime.datetime.strptime(lrequest.POST['dia_agendamento'], '%d/%m/%Y')
    lcheckin.save()
    lcheckin.canal.add(Canal.objects.get(id=lrequest.POST['canais']))

#pendente analisar adicionar_produto e remover_produto
@login_required
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
    loja_list = Loja.objects.filter(espaco__contrato__marca=checkin.marca).distinct()
    if len(request.POST) == 0 or request.POST['loja'] == '':
        espaco_list = None
        canal_list = None
        produto_list = None
        loja_retorno = None
    else:
        loja_retorno = Loja.objects.get(id=request.POST['loja'])
        checkin.loja_id = request.POST['loja']
        espaco_list = Espaco.objects.filter(contrato__marca=checkin.marca, loja_id=request.POST['loja']).distinct()
        canal_list = Canal.objects.all()
        cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, loja_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueLoja(checkin.marca, loja_retorno)
        expedicao = Expedicao()
        produto_list = checkin.marca.produto_set.all()
        contrato_list = Contrato.objects.filter(marca=checkin.marca, espaco__loja=loja_retorno)
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
                      'espaco_list':espaco_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'cubagem_contratada': cubagem_contratada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                      'loja_list': loja_list,
                      'loja_retorno': loja_retorno,
                      'contrato': contrato,
                  }
    )

@login_required
def edita_checkin(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    expedicao = Expedicao()

    if len(request.POST) != 0:
        loja_retorno = Loja.objects.get(id=request.POST['loja'])
        checkin.loja_id = request.POST['loja']
    else:
        loja_retorno = Loja.objects.get(id=checkin.loja_id)

    expedicao_list = Expedicao.objects.filter(checkin=checkin)

    loja_list = Loja.objects.filter(espaco__contrato__marca=checkin.marca).distinct()
    canal_list = Canal.objects.all()
    contrato_list = Contrato.objects.filter(marca=checkin.marca, espaco__loja=loja_retorno)
    if contrato_list.count() != 0:
      contrato = contrato_list[0]
    else:
      contrato = None

    cubagem_contratada = memoriacalculo.CubagemContratada(checkin.marca, loja_retorno)
    saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueLoja(checkin.marca, loja_retorno)

    espaco_list = Espaco.objects.filter(contrato__marca=checkin.marca, loja_id=checkin.loja_id).distinct()
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
                      'espaco_list': espaco_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                      'cubagem_contratada': cubagem_contratada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                      'loja_list': loja_list,
                      'loja_retorno': loja_retorno,
                      'contrato': contrato,
                  }
    )

@login_required
def dashboard_marca(request):
    return render (request,'dashboard_marca.html')

@login_required
def dashboard_operacional(request):
    return render (request, 'dashboard_operacional.html')

@login_required
def lista_checkin_operacional(request):
    checkin_list = Checkin.objects.all().exclude(status='emprocessamento')
    return render(request, 'lista_checkin_operacional.html', {'checkin_list': checkin_list})

@login_required
def edita_checkin_operacional(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    espaco_list = Espaco.objects.filter(contrato__marca=checkin.marca)
    canal_list = Canal.objects.all()

    expedicao = Expedicao()
    produto = Produto()
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = Expedicao.objects.filter(checkin=checkin)

    if request.method == 'POST':
        checkin.status = request.POST['statuscheckin']
        for expedicao in expedicao_list:
            expedicao.status = request.POST['status_produto_'+str(expedicao.produto.id)]
            if checkin.status == 'confirmado' and expedicao.status == 'ok':
                produto = Produto.objects.get(id=expedicao.produto.id)
                try:
                    estoque = Estoque.objects.get(produto=produto,loja=checkin.loja)
                    estoque.quantidade = estoque.quantidade + expedicao.quantidade
                    estoque.save()
                except Estoque.DoesNotExist:
                    estoque = Estoque()
                    estoque.produto = produto
                    estoque.loja = checkin.loja
                    estoque.quantidade = expedicao.quantidade
                    estoque.save()
                #produto.loja.add(checkin.loja(quantidade=expedicao.quantidade)
                #produto.quantidade += expedicao.quantidade
                #produto.save()

        checkin.save()

    return render(request, 'checkin_operacional.html',
                  {
                      'marca': checkin.marca,
                      'checkin': checkin,
                      'espaco_list': espaco_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                  }
    )

@login_required
def lista_checkout(request):
    checkout_list = Checkout.objects.all().exclude(motivo='venda')
    return render(request, 'lista_checkout.html', {'checkout_list': checkout_list})

def checkout(request):
    checkout = Checkout()
    marca_list = Marca.objects.all()
    loja_list = None
    produto_list = None
    marca_retorno = None
    loja_retorno = None
    produto_retorno = None
    checkout.motivo = request.GET.get('motivo')
    error = False
    estoque = None

    if request.method=='POST':
        checkout.motivo = request.POST['motivo']
        checkout.observacao = request.POST['observacao']
        checkout.marca = Marca.objects.get(id=request.POST['marca'])
        checkout.loja = Loja.objects.get(id=request.POST['loja'])
        checkout.produto = Produto.objects.get(id=request.POST['produto'])
        estoque = Estoque.objects.get(loja=checkout.loja,produto=checkout.produto)
        checkout.quantidade = int(request.POST['quantidade'])

        if estoque.quantidade < checkout.quantidade:
            marca_retorno = checkout.marca
            loja_list = Loja.objects.filter(espaco__contrato__marca=marca_retorno).distinct()
            loja_retorno = checkout.loja
            produto_list = marca_retorno.produto_set.filter(loja=loja_retorno)
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
            loja_list = Loja.objects.filter(espaco__contrato__marca=marca_retorno).distinct()
        if "marca" in request.GET and request.GET['marca'] != '' and "loja" in request.GET and request.GET['loja'] != '' :
            loja_retorno = Loja.objects.get(id=request.GET['loja'])
            produto_list = marca_retorno.produto_set.filter(loja=loja_retorno)
        if "marca" in request.GET and request.GET['marca'] != '' and "loja" in request.GET and request.GET['loja'] != '' and "produto" in request.GET and request.GET['produto'] != '':
            produto_retorno = Produto.objects.get(id=request.GET['produto'])


    return render(request,'checkout.html',
                 {
                     'marca_list':marca_list,
                     'loja_list':loja_list,
                     'produto_list':produto_list,
                     'marca_retorno':marca_retorno,
                     'loja_retorno':loja_retorno,
                     'produto_retorno':produto_retorno,
                     'checkout':checkout,
                     'error': error,
                     'estoque': estoque,
                  }
    )

@login_required
def estoque(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    loja_list = Loja.objects.filter(espaco__contrato__marca=marca).distinct()
    estoque = None
    loja_retorno = None
    estoque_list = None
    cubagem_contratada = 0
    saldo_cubagem_estoque = 0

    if request.method == 'GET' and "loja" in request.GET and request.GET['loja'] != '':
        estoque_list = Estoque.objects.filter(loja_id=request.GET['loja'], produto__marca=marca)
        loja_retorno = Loja.objects.get(id=request.GET['loja'])
        cubagem_contratada = memoriacalculo.CubagemContratada(marca, loja_retorno)
        saldo_cubagem_estoque = memoriacalculo.SaldoCubagemEstoqueLoja(marca, loja_retorno)

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque

    return render(request, 'estoque.html',
                  {
                      'marca': marca,
                      'loja_list': loja_list,
                      'estoque_list': estoque_list,
                      'loja_retorno': loja_retorno,
                      'cubagem_contratada': cubagem_contratada,
                      'saldo_cubagem_estoque': saldo_cubagem_estoque,
                      'saldo_cubagem': saldo_cubagem,
                  }
    )

@login_required
def estoque_operacional(request):
    marca = Marca.objects.get.all()
    loja_list = Loja.objects.filter(espaco__contrato__marca=marca).distinct()
    estoque = None
    loja_retorno = None
    estoque_list = None

    if request.method == 'GET' and "loja" in request.GET and request.GET['loja'] != '':
        estoque_list = Estoque.objects.filter(loja_id=request.GET['loja'], produto__marca=marca)
        loja_retorno = Loja.objects.get(id=request.GET['loja'])

    return render(request, 'estoque_operacional.html',
                  {
                      'marca': marca,
                      'loja_list': loja_list,
                      'estoque_list': estoque_list,
                      'loja_retorno': loja_retorno,
                  }
    )


def realizar_venda(request):
    checkout = Checkout()
    marca_list = Marca.objects.all()
    canal_list = Canal.objects.all()
    loja_list = None
    produto_list = None
    marca_retorno = None
    loja_retorno = None
    produto_retorno = None
    dtrealizado_retorno = None
    canal_retorno = None
    #checkout.motivo = request.GET.get('motivo')
    checkout.motivo = 'venda'
    error = False
    estoque = None

    if request.method=='POST':
        checkout.observacao = request.POST['observacao']
        checkout.marca = Marca.objects.get(id=request.POST['marca'])
        checkout.loja = Loja.objects.get(id=request.POST['loja'])
        checkout.produto = Produto.objects.get(id=request.POST['produto'])
        checkout.dtrealizado = datetime.datetime.strptime(request.POST['dtrealizado'], '%d/%m/%Y')
        checkout.canal = Canal.objects.get(id=request.POST['canal'])
        estoque = Estoque.objects.get(loja=checkout.loja,produto=checkout.produto)
        checkout.quantidade = int(request.POST['quantidade'])

        if estoque.quantidade < checkout.quantidade:
            marca_retorno = checkout.marca
            loja_list = Loja.objects.filter(espaco__contrato__marca=marca_retorno).distinct()
            loja_retorno = checkout.loja
            produto_list = marca_retorno.produto_set.filter(loja=loja_retorno)
            produto_retorno = checkout.produto
            canal_retorno = checkout.canal
            error = True

        else:
            estoque.quantidade = estoque.quantidade - checkout.quantidade
            estoque.save()
            checkout.save()
            return HttpResponseRedirect(reverse('realizar_venda'))
    else:
        if "dtrealizado" in request.GET:
            dtrealizado_retorno = request.GET['dtrealizado']
        if "canal" in request.GET:
            canal_retorno = Canal.objects.get(id=request.GET['canal'])
        if "marca" in request.GET and request.GET['marca'] != '':
            marca_retorno = Marca.objects.get(id=request.GET['marca'])
            loja_list = Loja.objects.filter(espaco__contrato__marca=marca_retorno).distinct()
        if "marca" in request.GET and request.GET['marca'] != '' and "loja" in request.GET and request.GET['loja'] != '' :
            loja_retorno = Loja.objects.get(id=request.GET['loja'])
            produto_list = marca_retorno.produto_set.filter(loja=loja_retorno)
        if "marca" in request.GET and request.GET['marca'] != '' and "loja" in request.GET and request.GET['loja'] != '' and "produto" in request.GET and request.GET['produto'] != '':
            produto_retorno = Produto.objects.get(id=request.GET['produto'])


    return render(request,'realizar_venda.html',
                 {
                     'marca_list':marca_list,
                     'loja_list':loja_list,
                     'produto_list':produto_list,
                     'marca_retorno':marca_retorno,
                     'loja_retorno':loja_retorno,
                     'produto_retorno':produto_retorno,
                     'dtrealizado_retorno':dtrealizado_retorno,
                     'checkout': checkout,
                     'error': error,
                     'estoque': estoque,
                     'canal_list': canal_list,
                     'canal_retorno': canal_retorno,
                  }
    )

@login_required
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
def acompanhar_venda(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    #loja
    loja_list = Loja.objects.filter(espaco__contrato__marca=marca).distinct()
    loja_retorno = None
    espaco_list = None
    periodo_list = None
    espaco_retorno = None
    periodo_retorno = None
    venda_list = None
    if len(request.POST) != 0:
        loja_retorno = Loja.objects.get(id=request.POST['loja'])
        if "espaco" in request.POST and request.POST['espaco'] != '':
            espaco_retorno = Espaco.objects.get(id=request.POST['espaco'])
        if "periodo" in request.POST and request.POST['periodo'] != '':
            periodo_retorno = Periodo.objects.get(id=request.POST['periodo'])
        # espaco
        espaco_list = Espaco.objects.filter(contrato__marca=marca, loja=loja_retorno).distinct()
        # periodo
        periodo_list = Periodo.objects.all()
        # venda (groupby produto, sum(qtd))
        venda_list = Checkout.objects.filter()

    return render(request, 'marca_acompanhar_venda.html',
                  {
                      'marca': marca,
                      'loja_list': loja_list,
                      'loja_retorno': loja_retorno,
                      'espaco_list': espaco_list,
                      'periodo_list': periodo_list,
                      'espaco_retorno': espaco_retorno,
                      'periodo_retorno': periodo_retorno,
                      'venda_list': venda_list,
                  }
    )
