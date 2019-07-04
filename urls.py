from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to, direct_to_template

#from haystack.views import SearchView, search_view_factory
#from haystack.forms import SearchForm

#from apps.ew_contact_form.forms import ContactForm
from views import LatestEntriesFeed

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^admin/cms/page/18/edit-plugin/[0-9]+/.*escapeHtml.*icon_src.*/$', 'django.views.defaults.page_not_found'),

    (r'^admin/surveys-editor/', include('apps.pollster.urls')),
    (r'^admin/users/', include('apps.sw_auth.urls_admin')),
    (r'^admin/tracking/', include('apps.reminder.urls_admin')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/tile/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)$', 'apps.pollster.views.map_tile', name='pollster_map_tile'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/click/(?P<lat>[\d.-]+)/(?P<lng>[\d.-]+)$', 'apps.pollster.views.map_click', name='pollster_map_click'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)\.json$', 'apps.pollster.views.chart_data', name='pollster_chart_data'),
    url(r'^surveys/(?P<shortname>.+)/$', 'apps.pollster.views.survey_run', name="survey_run"),
    (r'^survey/', include('apps.survey.urls')),
    (r'^reminder/', include('apps.reminder.urls')),
    (r'^influenzanet/', direct_to_template, {'template': 'influenzanet.html'}),
    (r'^cookies-policy/', direct_to_template, {'template': 'cookies-policy.html'}),

    (r'^rss/$', LatestEntriesFeed()),

    (r'^accounts/', include('apps.sw_auth.urls')),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),
    (r'^count/', include('apps.count.urls')),
    (r'^admin/top5/', include('apps.top5.urls_admin')),
    url(r'^top5/', include('apps.top5.urls')),
    url(r'^contact/$', redirect_to, {'url':'/contacts/'}, name='contact_form'),

    url(r'^register/$', 'apps.sw_auth.views.register_user', name='registration_register_explanation'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^404/$', 'django.views.defaults.page_not_found'),
        (r'^500/$', 'views.server_error'),
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls'), {'show_indexes': True}),
    ) + urlpatterns

if settings.MOBILE_INTERFACE_ACTIVE:
    urlpatterns += patterns('', (r'^ema/', include('apps.survey.api.urls')))

urlpatterns += patterns('',
    url(r'^municipal/', include('apps.municipal.urls')),
    url(r'^feedback/', include('apps.sw_feedback.urls')),
    url(r'^news/', include('apps.journal.urls')),
    url(r'^cohort/', include('apps.sw_cohort.urls')),
    url(r'^invite/', include('apps.sw_invitation.urls')),
    url(r'^dashboard/', include('apps.dashboard.urls')),
    url(r'^ascor/', include('apps.ascor.urls')),
)

# Catchall
urlpatterns += patterns('', url(r'^', include('cms.urls')))

handler500 = 'views.server_error'
