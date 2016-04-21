from django.template.defaulttags import register

@register.simple_tag(takes_context=True)
def getpreco(context, precodevenda, canalpercentualdeflacao, canalabsolutodeflacao, canalacumulativo, lojapercentualdeflacao, lojaabsolutodeflacao):
    if canalacumulativo == 0:
        context['precocalculado'] = (precodevenda*(100 - canalpercentualdeflacao)/100 - canalabsolutodeflacao)
    else:
        context['precocalculado'] = precodevenda*(100 - canalpercentualdeflacao - lojapercentualdeflacao)/100 - canalabsolutodeflacao - lojaabsolutodeflacao
    return ''
