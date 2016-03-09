from django.shortcuts import render
from models import Produto
from administrativo.models import Marca
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from operacional.forms import LoginForm, ProdutoForm
from django import forms
from django.contrib.auth.decorators import login_required

# Create your views here.

def login_marca(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            senha = request.POST['senha']
            user = authenticate(username=username, password=senha)
            if user != None:
                login(request, user)
                marca = Marca.objects.get(user=request.user)
                #marcaS = serializers.serialize("json", [marca])
                #request.session['marca'] = marcaS
                request.session['marca_id'] = marca.id
                # return HttpResponse('usuario logado')
                return HttpResponseRedirect('/marca/listaprodutos/')
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
def cadastra_produto(request,template_name ):
    marca = Marca.objects.get(id=request.session['marca_id'])
    produto_cadastado = False
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = Produto(nome=request.POST['nome'],altura=request.POST['altura'],largura=request.POST['largura'],profundidade=request.POST['profundidade'],marca=marca)
            produto.save()
            produto_cadastado = True
            return render(request,template_name,{'form':form,'marca':marca, 'produto_cadastrado':produto_cadastado})
        else:
            raise forms.ValidationError("Algum nome ou id incoerrente com o formulario")
    else:
        form = ProdutoForm()
        return render(request,template_name,{'form':form,'marca':marca, 'produto_cadastrado':produto_cadastado})