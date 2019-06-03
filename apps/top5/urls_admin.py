from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^html_creation/(?P<service_id>\d+)/$', views.create_service_html, name='top5_create_html'),
    url(r'^calcul_score/(?P<service_id>\d+)/$', views.calcul_score, name='top5_calcul_score'),
)


