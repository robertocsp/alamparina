from django.conf.urls import patterns, include, url
from django.contrib import admin
from alamparina.views import usuario_marca
from operacional.views import *
#from alamparina.views import login_marca

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alamparina.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # ...
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuariomarca/$', usuario_marca),
    url(r'^login/$', login_operacional, name='login_operacional'),
    url(r'^marca/dashboard/$', dashboard_marca, name='dashboard_marca'),
    url(r'^operacional/dashboard/$', dashboard_operacional, name='dashboard_operacional'),
    url(r'^marca/listaprodutos/$', lista_produtos, name='lista_produtos'),
    url(r'^marca/cadastra-produto/(?P<id>\d+)/$', edita_produto, name='marca_edita_produto'),
    url(r'^marca/cadastra-produto/$', cadastra_produto, name='marca_cadastra_produto'),
    url(r'^marca/lista-checkin/$', lista_checkin, name='lista_checkin'),
    url(r'^marca/checkin/$', inicia_checkin, name='inicia_checkin'),
    url(r'^marca/checkin/(?P<id>\d+)/$', edita_checkin, name='edita_checkin'),
    url(r'^operacional/lista-checkin/$', lista_checkin_operacional, name='lista_checkin_operacional'),
    url(r'^operacional/checkin/(?P<id>\d+)/$', edita_checkin_operacional, name='edita_checkin_operacional'),
    url(r'^marca/estoque/$', estoque, name='estoque'),
    url(r'^operacional/lista-checkout/$', lista_checkout, name='lista_checkout'),
    url(r'^operacional/checkout/$', checkout, name='checkout'),
    url(r'^operacional/realizar-venda/$', realizar_venda, name='realizar_venda'),
    #url(r'^marca/listaprodutos2/$', ProdutoList.as_view(template_name="lista_produtos-old.html")),

    # ...
)
