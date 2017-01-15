from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from alamparina.views import usuario_marca
from operacional.views import *
from operacional import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alamparina.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # ...
    url(r'^api/get_prod/$', views.get_prod),
    url(r'^api/get_prod_marca/$', views.get_prod_marca),
    url(r'^$', login_geral, name='login_geral'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^change-password/', 'django.contrib.auth.views.password_change', {'post_change_redirect': '/password-changed/'}),
    url(r'^login/$', login_geral, name='login_geral'),
    url(r'^logout/$', views.Logout),
    url(r'^marca/acompanhar-venda/$', acompanhar_venda, name='acompanhar_venda'),
    url(r'^marca/cadastra-produto/$', cadastra_produto, name='marca_cadastra_produto'),
    url(r'^marca/cadastra-produto/(?P<id>\d+)/$', edita_produto, name='marca_edita_produto'),
    url(r'^marca/checkin/$', inicia_checkin, name='inicia_checkin'),
    url(r'^marca/checkin/(?P<id>\d+)/$', edita_checkin, name='edita_checkin'),
    url(r'^marca/dashboard/$', dashboard_marca, name='dashboard_marca'),
    url(r'^marca/estoque/$', estoque, name='estoque'),
    url(r'^marca/importacao/$', importacao, name='importacao'),
    url(r'^marca/listaprodutos/$', lista_produtos, name='lista_produtos'),
    url(r'^marca/lista-checkin/$', lista_checkin, name='lista_checkin'),
    url(r'^marca/recomendar-marca/$', recomendar_marca, name='recomendar_marca'),
    url(r'^operacional/acompanhar-vendas/$', acompanhar_vendas_operacional, name='acompanhar_vendas_operacional'),
    url(r'^operacional/checkin/(?P<id>\d+)/$', edita_checkin_operacional, name='edita_checkin_operacional'),
    url(r'^operacional/checkout/$', checkout, name='checkout'),
    url(r'^operacional/dashboard/$', dashboard_operacional, name='dashboard_operacional'),
    url(r'^operacional/estoque/$', estoque_operacional, name='estoque_operacional'),
    url(r'^operacional/lista-checkin/$', lista_checkin_operacional, name='lista_checkin_operacional'),
    url(r'^operacional/lista-checkout/$', lista_checkout, name='lista_checkout'),
    url(r'^operacional/lista-produtos/$', lista_produtos_operacional, name='lista_produtos_operacional'),
    url(r'^operacional/realizar-venda/$', inicia_realizar_venda, name='inicia_realizar_venda'),
    url(r'^operacional/realizar-venda/(?P<id>\d+)/$', edita_realizar_venda, name='edita_realizar_venda'),
    url(r'^password-changed/', 'django.contrib.auth.views.password_change_done'),
    url(r'^usuariomarca/$', usuario_marca)
    #url(r'^marca/listaprodutos2/$', ProdutoList.as_view(template_name="lista_produtos-old.html")),
    # ...
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

