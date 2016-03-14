from django.shortcuts import render, render_to_response
from models import Produto
from administrativo.models import Marca
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from operacional.models import Checkin, Expedicao
from operacional.forms import *
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
# Create your views here.

def login_marca(request):
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
    marca = Marca.objects.get(id=request.session['marca_id'])
    produto_cadastado = True
    produto = get_object_or_404(Produto, id=id)
    return HttpResponseRedirect(reverse('marca_cadastra_produto'))

@login_required
def lista_checkin(request):
    return render(request, 'lista_checkin.html')

@login_required
def realiza_checkin(request):
    checkin = Checkin()
    expedicao = Expedicao()
    checkin.tipo = 'chin'
    checkin.marca = Marca.objects.get(id=request.session['marca_id'])
    checkin.status = 'enviado'
    produto_list = checkin.marca.produto_set.all()
    expedicao_list = None

    if request.method == 'POST':
        form = CheckinForm(request.POST)
        if form.is_valid():
            form.save(marca)

    else:
        form = CheckinForm()

    return render(request,'checkin.html',
                  {
                      'marca': checkin.marca,
                      'produto_list':produto_list,
                      'checkin':checkin,
                      'expedicao':expedicao_list,
                      'form' : form
                  }
    )