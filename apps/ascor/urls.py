from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='ascor_index'),
)