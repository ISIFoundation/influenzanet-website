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

#    (r'^googlec96088c11ef7e5c4.html$', 'django.views.generic.simple.direct_to_template', {'template': 'googlec96088c11ef7e5c4.html'}),
#    (r'nu.html$', 'django.views.generic.simple.direct_to_template', {'template': 'nu.html'}),

#    (r'^mobile/login/$', 'apps.sw_auth.mobile.mobile_login'),
    (r'^mobile/surveys/(?P<shortname>.+)/$', 'apps.pollster.views.survey_run', {'clean_template': True, 'next': '/mobile/success/'}),
#    (r'^mobile/surveys/(?P<shortname>.+)/$', 'django.views.generic.simple.direct_to_template', {'template': 'survey/mobile_success.html'}),
    (r'^mobile/success/$', direct_to_template , {'template': 'survey/mobile_success.html'}),
    (r'^mobile/map/(?P<survey_shortname>.+)/(?P<chart_shortname>.+)/$', 'apps.pollster.views.survey_map'),
#    (r'^mobile/login/$', 'views.mobile_login'),
#    (r'^mobile/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 'apps.journal.views.entry', {'template_name': 'mobile'}),
#    (r'^mobile/rss/$', LatestEntriesFeed()),

    (r'^rss/$', LatestEntriesFeed()),

#    url(r'^captcha/', include('captcha.urls')),
    #(r'^tellafriend/', include('tellafriend.urls')),

#    url(r'^search/$', search_view_factory(
#        view_class=SearchView,
#        form_class=SearchForm
#    ), name='haystack_search'),

#    (r'^test-search/$', 'views.test_search'),
    (r'^accounts/', include('apps.sw_auth.urls')),
    url(r'^login/$', redirect_to, {'url': settings.LOGIN_URL}, name='loginurl-index'),
    (r'^login/', include('loginurl.urls')),
    (r'^count/', include('apps.count.urls')),
#    (r'^contest/', include('apps.contest.urls')),

    url(r'^contact/$', redirect_to, {'url':'/contacts/'}, name='contact_form'),

#    url(r'^contact/$', 'contact_form.views.contact_form', {'form_class': ContactForm}, name='contact_form'),
#    url(r'^contact/sent/$', 'django.views.generic.simple.direct_to_template', {'template': 'contact_form/contact_form_sent.html'}, name='contact_form_sent'),

#    (r'^colors.css$', 'apps.partnersites.views.colors_css'),

    url(r'^register/$', 'apps.sw_auth.views.register_user', name='registration_register_explanation'),

#    (r'^forum/', include('pybb.urls', namespace='pybb')),

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
)

# Catchall
urlpatterns += patterns('', url(r'^', include('cms.urls')))

handler500 = 'views.server_error'
