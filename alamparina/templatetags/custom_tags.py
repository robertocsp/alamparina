from django.template.defaulttags import register
from alamparina.library import memoriacalculo
import datetime

@register.simple_tag(takes_context=True)
def getPrecoEstimado(context, produto, canal, contrato):
    context['precoestimado'] = memoriacalculo.PrecoEstimado(produto, canal, contrato)
    return ''

@register.simple_tag(takes_context=True)
def Multiplicacao(context, a, b):
    context['calculado'] = float(a or 0)*float(b or 0)
    return ''

@register.simple_tag(takes_context=True)
def DiferencaData(context, a):
    context['calculado'] = False
    if a != None:
        diferenca = datetime.date.today() - a
        if diferenca < datetime.timedelta(days=60):
            context['calculado'] = True
    return ''
