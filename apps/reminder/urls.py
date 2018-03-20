from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings
from . import views

from loginurl.views import cleanup, login

urlpatterns = patterns('apps.reminder.views',
    (r'^latest_newsletter/$', 'latest_newsletter'),
    url(r'^tracking/(?P<id_tracking>.+)/$',  views.tracking_url, name='tracking'),
    (r'^unsubscribe/$', 'unsubscribe'),
    (r'^resubscribe/$', 'resubscribe'),
    (r'^overview/$', 'overview'),
    (r'^manage/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<hour>[0-9]+)/(?P<minute>[0-9]+)/$', 'manage'),
    (r'^preview/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<hour>[0-9]+)/(?P<minute>[0-9]+)/$', 'preview'),
)


