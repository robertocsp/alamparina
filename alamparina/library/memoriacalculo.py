from operacional.models import Estoque, Produto
from administrativo.models import TipoMiniloja, Miniloja

# Saldo da Cubagem:
def CubagemContratada(marca, unidade):
    cubagem_contratada = 0
    miniloja_list = Miniloja.objects.filter(contrato__marca=marca, unidade=unidade).distinct()
    for miniloja in miniloja_list:
        tipominiloja = TipoMiniloja.objects.get(id=miniloja.tipo_id)
        tipominiloja.volume = tipominiloja.largura * tipominiloja.altura * tipominiloja.profundidade
        cubagem_contratada += tipominiloja.volume
    return cubagem_contratada

# Saldo da Cubagem:
# Geral de produto no estoque, saldo dele em todas as unidades somadas.
def SaldoCubagemEstoqueProduto(produto):
    saldo_cubagem_estoque_produto = 0
    estoque_list = Estoque.objects.filter(produto=produto)
    if len(estoque_list) > 0:
        for estoque in estoque_list:
            saldo_cubagem_estoque_produto += estoque.quantidade * produto.largura * produto.altura * produto.profundidade
    return saldo_cubagem_estoque_produto

# Saldo da Cubagem:
# Geral da unidade, de acordo com a marca
def SaldoCubagemEstoqueUnidade(marca, unidade):
    saldo_cubagem_estoque_unidade = 0
    produto_list = Produto.objects.filter(marca=marca)
    if len(produto_list) > 0:
        for produto in produto_list:
            estoque_list = Estoque.objects.filter(unidade=unidade, produto=produto)
            if len(estoque_list) > 0:
                for estoque in estoque_list:
                    saldo_cubagem_estoque_unidade += estoque.quantidade * produto.largura * produto.altura * produto.profundidade
    return saldo_cubagem_estoque_unidade

def PrecoEstimado(produto, canal, contrato):
    if canal.acumulativo == 0:
        preco_estimado = (produto.preco_venda*(100 - canal.percentual_deflacao)/100 - int(canal.custo_embalagem or 0) - int(canal.custo_entrega or 0))
    else:
        preco_estimado = produto.preco_venda*(100 - float(canal.percentual_deflacao or 0) - float(contrato.percentual_deflacao or 0))/100 - int(canal.custo_embalagem or 0) - int(canal.custo_entrega or 0) - int(contrato.custo_embalagem or 0) - int(contrato.custo_entrega or 0)
    return preco_estimado

def PrecoReceber(checkout, contrato):
    if checkout.canal.acumulativo == 0:
        preco_receber = (float(checkout.preco_venda or 0)*(100 - float(checkout.canal.percentual_deflacao or 0))/100 - int(checkout.canal.custo_embalagem or 0) - int(checkout.canal.custo_entrega or 0))
    else:
        preco_receber = float(checkout.preco_venda or 0)*(100 - float(checkout.canal.percentual_deflacao or 0) - float(contrato.percentual_deflacao or 0))/100 - int(checkout.canal.custo_embalagem or 0) - int(checkout.canal.custo_entrega or 0) - int(contrato.custo_embalagem or 0) - int(contrato.custo_entrega or 0)
    return preco_receber