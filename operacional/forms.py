from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    senha = forms.CharField(max_length=20,widget=forms.PasswordInput)


class ProdutoForm(forms.Form):
    nome = forms.CharField(max_length=100)
    largura = forms.CharField(max_length=10)
    altura = forms.CharField(max_length=10)
    profundidade = forms.CharField(max_length=10)