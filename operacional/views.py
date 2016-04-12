# -*- coding: utf-8 -*-
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

@login_required
def inicia_checkin(request):
    checkin = Checkin()
    checkin.tipo = 'chin'
    checkin.marca = Marca.objects.get(id=request.session['marca_id'])
    checkin.status = 'emprocessamento'
    #Espaco e canal
    espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca)
    canal_list = Canal.objects.all()

    #produtos
    expedicao = Expedicao()
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = None

    if "adicionar_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento =datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        checkin.save()
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento = datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        checkin.save()
        expedicao.produto = produto

        #loop de canal, para calcular o preco
        for canal in canal_list:
            canal.precificacao = expedicao.produto.preco_venda*(100-canal.percentual_deflacao)/100-canal.absoluto_deflacao

        expedicao.checkin = checkin
        expedicao.save()
        return HttpResponseRedirect('/marca/checkin/' + str(checkin.id))

    elif "finalizar" in request.POST:
        messages.error(request, 'Não existe nenhum produto inserido')

    return render(request,'checkin.html',
                  {
                      'marca': checkin.marca,
                      'checkin':checkin,
                      'espaco_list':espaco_list,
                      'canal_list': canal_list,
                      'produto_list': produto_list,
                      'expedicao_list': expedicao_list,
                  }
    )

@login_required
def edita_checkin(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    espaco_list = Espaco.objects.filter(alocacao__marca=checkin.marca)
    canal_list = Canal.objects.all()

    expedicao = Expedicao()
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = Expedicao.objects.filter(checkin=checkin)

    if "adicionar_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento =datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        checkin.save()

    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento = datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        expedicao.produto = produto

        #loop de canal, para calcular o preco
        for canal in canal_list:
            canal.precificacao = expedicao.produto.preco_venda*(100-canal.percentual_deflacao)/100-canal.absoluto_deflacao

        expedicao.checkin = checkin
        checkin.save()
        expedicao.save()

    elif "finalizar" in request.POST:
        if expedicao_list == None:
            messages.error(request, 'Não existe nenhum produto inserido')
        else:
            checkin.status = checkin.status_enviado()
            checkin.save()

    return render(request, 'checkin.html',
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
def dashboard_marca(request):
    return render (request,'dashboard_marca.html')

@login_required
def estoque(request):
    marca = Marca.objects.get(id=request.session['marca_id'])
    produto_list = Produto.objects.filter(marca__id=marca.id, em_estoque='sim')
    return render(request, 'estoque.html', {'produto_list': produto_list, 'marca': marca})

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
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = Expedicao.objects.filter(checkin=checkin)

    if "adicionar_canal" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento =datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        checkin.canal.add(Canal.objects.get(id=request.POST['canais']))
        checkin.save()

    elif "adicionar_produto" in request.POST:
        checkin.dia_agendamento = datetime.datetime.strptime(request.POST['dia_agendamento'], '%d/%m/%Y')
        checkin.hora_agendamento = datetime.datetime.strptime(request.POST['hora_agendamento'], '%H:%M')
        produto = Produto.objects.get(id=request.POST['produtos'])
        expedicao.quantidade = request.POST['qtde_produto']
        expedicao.produto = produto
        expedicao.checkin = checkin
        checkin.save()
        expedicao.save()

    elif "finalizar" in request.POST:
        if expedicao_list == None:
            messages.error(request, 'Não existe nenhum produto inserido')
        else:
            checkin.status = checkin.status_enviado()
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