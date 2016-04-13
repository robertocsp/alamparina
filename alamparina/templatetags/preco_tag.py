from django.template.defaulttags import register

@register.simple_tag(takes_context=True)
def getpreco(context, precodevenda, percentualdeflacao, absolutodeflacao):
    context['precocalculado'] = (precodevenda*(100 - percentualdeflacao)/100 - absolutodeflacao)
    return ''
