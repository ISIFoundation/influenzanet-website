from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^html_creation/(?P<service_id>\d+)/$', views.create_service_html, name='top5_create_html'),
    url(r'^calcul_score/(?P<service_id>\d+)/$', views.calcul_score, name='top5_calcul_score'),
    url(r'^all_calculs/$', views.all_calculs, name='top5_all_calculs'),
    url(r'^results/$', views.survey_results_csv, name='top5_results'),
    url(r'^info_participants/$', views.survey_participants_csv, name='top5_participants'),
)



