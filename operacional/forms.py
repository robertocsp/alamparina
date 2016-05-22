from django import forms
from operacional.models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    senha = forms.CharField(max_length=20,widget=forms.PasswordInput)


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        exclude = ['marca','codigo','quantidade','preco_base','em_estoque', 'unidade', 'miniloja']
        widgets = {
            'descricao': forms.Textarea
        }

    def __init__(self, *args, **kwargs):
        super(ProdutoForm, self).__init__(*args, **kwargs)
        self.fields['largura'].widget.attrs['class'] = 'numero'
        self.fields['altura'].widget.attrs['class'] = 'numero'
        self.fields['profundidade'].widget.attrs['class'] = 'numero'
        self.fields['preco_venda'].widget.attrs['class'] = 'numero'
        self.fields['peso'].widget.attrs['class'] = 'numero'
        self.fields['estoque_minimo'].widget.attrs['class'] = 'numero'
        self.fields['garantia'].widget.attrs['class'] = 'numero'

class CheckinForm(forms.Form):
    dia_agendamento = forms.DateField(label='Dia agendamento')
    hora_agendamento = forms.TimeField(label='Hora agendamento')
    produtos = forms.ChoiceField(label='Produtos')
    qtde_produto = forms.IntegerField(label='Quantidade')

    def save(self, marca):
        checkin.dia_agendamento = self.cleaned_data.get('dia_agendamento')
        checkin.hora_agendamento = self.cleaned_data.get('hora_agendamento')
        marca = marca
        #expedicao.checkin = checkin
        #expedicao_list = expedicao.produto_set.all()

class RecomendacaoForm(forms.ModelForm):
    class Meta:
        model = Recomendacao
        exclude = ['marca']
        widgets = {
            'comentario' : forms.Textarea
        }