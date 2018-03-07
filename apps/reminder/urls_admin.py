from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^follow/(?P<newsletter_id>\d+)/$', views.follow_sending, name='reminder_follow_sending'),
)


