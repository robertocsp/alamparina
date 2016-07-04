from administrativo.models import Marca
from django.contrib.auth.models import Permission, User


def ValidaAcesso(lrequest, lmarca):
    erro = ''
    usuario = User.objects.get(id=lrequest.user.pk)
    marca = Marca.objects.get(user=usuario)
    if marca.id != lmarca.id:
        erro = "Acesso Negado."
    return erro
