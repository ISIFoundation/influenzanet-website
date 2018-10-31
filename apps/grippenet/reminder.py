from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.translation import activate

from apps.common.mail import create_message_from_template


import loginurl.utils
from apps.partnersites.context_processors import site_context

import datetime

def get_login_url(user, next):
    expires = datetime.datetime.now() + datetime.timedelta(days=30)

    usage_left = 5
    key = loginurl.utils.create(user, usage_left, expires, next)

    domain = Site.objects.get_current()
    path = reverse('loginurl-index').strip('/')
    loginurl_base = 'https://%s/%s' % (domain, path)

    return '%s/%s' % (loginurl_base, key.key)

def create_reminder_message(user, next=None, template_name='reminder', wrap_layout=True):

    activate('fr')

    c = {
        'url': get_login_url(user, next),
    }

    c.update(site_context())

    site_url = 'https://%s' % Site.objects.get_current().domain
    media_url = '%s%s' % (site_url, settings.MEDIA_URL)

    c['site_url'] = site_url
    c['MEDIA_URL'] = media_url

    return create_message_from_template(template_name, c, wrap_layout=wrap_layout)