from django.template.defaulttags import register
from alamparina.library import memoriacalculo

@register.simple_tag(takes_context=True)
def getPrecoEstimado(context, produto, canal, loja):
    context['precoestimado'] = memoriacalculo.PrecoEstimado(produto, canal, loja)
    return ''
