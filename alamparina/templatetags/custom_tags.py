from django.template.defaulttags import register
from alamparina.library import memoriacalculo

@register.simple_tag(takes_context=True)
def getPrecoEstimado(context, produto, canal, contrato):
    context['precoestimado'] = memoriacalculo.PrecoEstimado(produto, canal, contrato)
    return ''
