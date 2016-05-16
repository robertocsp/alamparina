from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from alamparina.views import usuario_marca
from operacional.views import *
from operacional import views
#from alamparina.views import login_marca

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alamparina.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # ...
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuariomarca/$', usuario_marca),
    url(r'^login/$', login_geral, name='login_geral'),
    url(r'^logout/$', views.Logout),
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
    url(r'^marca/acompanhar-venda/$', acompanhar_venda, name='acompanhar_venda'),
    url(r'^marca/recomendar-marca/$', recomendar_marca, name='recomendar_marca'),
    url(r'^operacional/lista-produtos/$', lista_produtos_operacional, name='lista_produtos_operacional'),
    url(r'^operacional/estoque/$', estoque_operacional, name='estoque_operacional')
    #url(r'^marca/listaprodutos2/$', ProdutoList.as_view(template_name="lista_produtos-old.html")),
    # ...
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

