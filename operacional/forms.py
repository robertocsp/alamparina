from django import forms
from operacional.models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    senha = forms.CharField(max_length=20,widget=forms.PasswordInput)


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'largura', 'altura', 'profundidade']

class CheckinForm(forms.Form):
    dia_agendamento = forms.DateField(label='dia_agendamento', input_formats='d/m/Y')
    hora_agendamento = forms.TimeField(label='hora_agendamento',input_formats='%H:%M')
    produtos = forms.ChoiceField(label='produtos')
    qtde_produto = forms.IntegerField(label='qtde_produto')

    def save(self, marca):
        checkin.dia_agendamento = self.cleaned_data.get('dia_agendamento')
        checkin.hora_agendamento = self.cleaned_data.get('hora_agendamento')
        marca = marca
        #expedicao.checkin = checkin
        #expedicao_list = expedicao.produto_set.all()


