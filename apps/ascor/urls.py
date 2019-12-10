from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='ascor_index'),
    url(r'^user/participants/$', views.user_participants, name='ascor_user_participants'),
    url(r'^user/participant/$', views.user_participant, name='ascor_user_participant'),
    url(r'^formulaire/$', views.formulaire, name='ascor_formulaire'),
)