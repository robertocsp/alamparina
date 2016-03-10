from django.conf.urls import patterns, include, url
from django.contrib import admin
from alamparina.views import usuario_marca
from operacional.views import lista_produtos, login_marca, cadastra_produto, realiza_checkin
#from alamparina.views import login_marca

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alamparina.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # ...
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usuariomarca/$', usuario_marca),
    url(r'^marca/login/$', login_marca, name='login_marca'),
    url(r'^marca/listaprodutos/$', lista_produtos, name='lista_produtos'),
    url(r'^marca/cadastra-produto/$', cadastra_produto, {'template_name':'marca_cadastra_produto.html'}),
    url(r'^marca/checkin/$', realiza_checkin, name='realiza_checkin'),
    #url(r'^marca/listaprodutos2/$', ProdutoList.as_view(template_name="lista_produtos-old.html")),

    # ...
)
