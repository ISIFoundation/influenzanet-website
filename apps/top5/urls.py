# -*- coding: utf-8 -*-
from django.views.generic.simple import redirect_to
from django.conf.urls.defaults import *
from django.conf import settings
from . import views

urlpatterns = patterns('apps.top5.views',
    url(r'^$', views.index, name='top5_index'),
    url(r'^selection_service/$', views.selection_service, name='top5_selection_service'),
    url(r'creation_rank/$', views.creation_rank , name='top5_creation_rank_service'),
    url(r'chgmt_statut_service/$', 'chgmt_statut_service', name='top5_chmgt_statut_service'),
    url(r'^ranking/$', views.ranking, name='top5_ranking'),
    url(r'^save/$', views.saving_rank, name='top5_save_rank'),

    url(r'^admins/$', include('apps.top5.urls_admin')),
)



