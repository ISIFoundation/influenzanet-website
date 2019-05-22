from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^html_creation/(?P<service_id>\d+)/$', views.create_service_html, name='top5_create_html'),
)


