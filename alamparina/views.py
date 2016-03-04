from django.http import HttpResponse
from administrativo.models import Marca
from django.contrib.auth.decorators import login_required

@login_required
def usuario_marca(request):
    marca = Marca.objects.get(user=request.user)
    return HttpResponse('username: ' + request.user.username + ' // marca : ' + marca.nome)