# -*- coding: utf-8 -*-
from distutils.command.check import check

from django.shortcuts import render, render_to_response
from models import Produto
from models import Canal
from administrativo.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from operacional.forms import *
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
# Create your views here.
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
def cadastra_produto(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.marca = marca
            produto.save()
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
            produto.save()
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

#variáveis globais
volume_checkin = 0.0
gcheckinid = 0
@login_required
def inicia_checkin(request):
    checkin = Checkin()
    checkin.tipo = 'chin'
    checkin.marca = Marca.objects.get(id=request.session['marca_id'])
    checkin.status = 'emprocessamento'
    # obtenho lojas
    cubagem_contratada = 0
    saldo_cubagem_estoque = 0
    expedicao_list = None
    loja_list = Loja.objects.filter(espaco__alocacao__marca=checkin.marca).distinct()

    if len(request.POST) == 0 or request.POST['loja'] == '':
        espaco_list = None
        canal_list = None
        volumeprodutos_list = None
        produto_list = None
        loja_retorno = None
    else:
        #Espaco e canal
        loja_retorno = Loja.objects.get(id=request.POST['loja'])
        checkin.loja_id = request.POST['loja']
        #espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca)
        #Espaco: filtrar por marca e por loja
        espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca, loja_id=request.POST['loja']).distinct()
        canal_list = Canal.objects.all()
        # Cubagem_contratada
        for espaco in espaco_list:
            tipoespaco = TipoEspaco.objects.get(id=espaco.tipo_id)
            tipoespaco.volume = tipoespaco.largura * tipoespaco.altura * tipoespaco.profundidade
            cubagem_contratada += tipoespaco.volume
        # Saldo da Cubagem em Estoque
        estoque_list = Estoque.objects.filter(loja_id=request.POST['loja'])
        for estoque in estoque_list:
            volumeproduto = Produto.objects.get(id=estoque.produto_id, em_estoque='sim')
            saldo_cubagem_estoque += estoque.quantidade * volumeproduto.largura * volumeproduto.altura * volumeproduto.profundidade

        # produtos
        expedicao = Expedicao()
        produto_list = checkin.marca.produto_set.all()

    global volume_checkin
    global gcheckinid
    if gcheckinid != 0:
        volume_checkin = 0

    if "adicionar_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.save()
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    #nao deve precisar desse elif remover_canal visto que:
    # sempre que inicia esta vazio. Depois que faz-se a primeira inclusao de canal
    # ele passa a ir no "edita_checkin"
    elif "remover_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.save()
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    #acho que nunca passa aqui, ver com o Roberto
    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        checkin.save()
        expedicao.produto = produto
        volume_checkin += int(expedicao.quantidade) * produto.altura * produto.largura * produto.profundidade
        expedicao.checkin = checkin
        expedicao.save()
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    #análogo ao remover_canal, ver comentário de lá
    elif "remover_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        checkin.save()
        expedicao.produto = produto
        global volume_checkin
        volume_checkin += int(expedicao.quantidade) * produto.altura * produto.largura * produto.profundidade
        expedicao.checkin = checkin
        expedicao.save()
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    #elif "filtrar_lojas" in request.POST:
        #return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "finalizar" in request.POST:
        messages.error(request, 'Não existe nenhum produto inserido')

    saldo_cubagem = cubagem_contratada - saldo_cubagem_estoque + volume_checkin

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
                      'volume_checkin': volume_checkin,
                      'saldo_cubagem': saldo_cubagem,
                      'loja_list': loja_list,
                      'loja_retorno': loja_retorno,
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

    loja_list = Loja.objects.filter(espaco__alocacao__marca=checkin.marca).distinct()
    canal_list = Canal.objects.all()

    cubagem_contratada = 0
    saldo_cubagem_estoque = 0

    espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca, loja_id=checkin.loja_id).distinct()
    produto_list = checkin.marca.produto_set.all()
    #Cubagem_contratada
    for espaco in espaco_list:
        tipoespaco = TipoEspaco.objects.get(id=espaco.tipo_id)
        tipoespaco.volume = tipoespaco.largura * tipoespaco.altura * tipoespaco.profundidade
        cubagem_contratada += tipoespaco.volume
    # Saldo da Cubagem em Estoque
    estoque_list = Estoque.objects.filter(loja_id=checkin.loja_id)
    for estoque in estoque_list:
        volumeproduto = Produto.objects.get(id=estoque.produto_id, em_estoque='sim')
        saldo_cubagem_estoque += estoque.quantidade * volumeproduto.largura * volumeproduto.altura * volumeproduto.profundidade

    #quando muda o checkin, preciso zerar a variavel de volume de checkin previsto (volume_checkin)
    if gcheckinid != id:
        global gcheckinid
        gcheckinid = id
        volume_checkin = 0
        exp_list = Expedicao.objects.filter(checkin=checkin)
        for exp in exp_list:
            prod = Produto.objects.get(id=exp.produto_id)
            volume_checkin += int(exp.quantidade) * prod.altura * prod.largura * prod.profundidade

    if "adicionar_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        checkin.save()


    elif "remover_canal" in request.POST:
        checkin.canal.remove(Canal.objects.get(id=request.POST['canais']))
        checkin.save()

    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        expedicao.produto = produto
        global volume_checkin
        volume_checkin += int(expedicao.quantidade) * produto.altura * produto.largura * produto.profundidade
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
                #volume_checkin -= int(request.POST['qtde_produto']) * produto.altura * produto.largura * produto.profundidade
                expedicao_remove.save()
                checkin.save()
            elif expedicao_remove.quantidade == int(request.POST['qtde_produto']):
                #volume_checkin -= int(request.POST['qtde_produto']) * produto.altura * produto.largura * produto.profundidade
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
                      'volume_checkin': volume_checkin,
                      'saldo_cubagem': saldo_cubagem,
                      'loja_list': loja_list,
                      'loja_retorno': loja_retorno,
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
    espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca)
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
                produto.quantidade += expedicao.quantidade
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
        quantidade = int(request.POST['quantidade'])

        if estoque.quantidade < quantidade:
            marca_retorno = checkout.marca
            loja_list = Loja.objects.filter(espaco__alocacao__marca=marca_retorno).distinct()
            loja_retorno = checkout.loja
            produto_list = marca_retorno.produto_set.filter(loja=loja_retorno)
            produto_retorno = checkout.produto

            error = True

        else:
            estoque.quantidade = estoque.quantidade - quantidade
            estoque.save()
            checkout.save()
            return HttpResponseRedirect(reverse('lista_checkout'))
    else:
        if "marca" in request.GET and request.GET['marca'] != '':
            marca_retorno = Marca.objects.get(id=request.GET['marca'])
            loja_list = Loja.objects.filter(espaco__alocacao__marca=marca_retorno).distinct()
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
    loja_list = Loja.objects.filter(espaco__alocacao__marca=marca).distinct()
    estoque = None
    loja_retorno = None
    estoque_list = None

    if request.method == 'GET' and "loja" in request.GET and request.GET['loja'] != '':
        estoque_list = Estoque.objects.filter(loja_id=request.GET['loja'], produto__marca=marca)
        loja_retorno = request.GET['loja']

    return render(request, 'estoque.html',
                  {
                      'marca': marca,
                      'loja_list': loja_list,
                      'estoque_list': estoque_list,
                      'loja_retorno':loja_retorno,
                  }
    )


