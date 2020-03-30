from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.conf import settings as django_settings
from cms.utils.html import clean_html

from .models import SiteSettings

def customizations(request):
    return site_context()

def site_context(with_url=False):
    site = Site.objects.get_current()
    settings = SiteSettings.get(site)

    data = {
        'site_name': site.name,
        'site_logo': getattr(django_settings, 'SITE_LOGO', ''),
        'site_headline': getattr(django_settings, 'SITE_HEADLINE', ""),
        'site_icon': getattr(django_settings, 'SITE_ICON', ''),
        'contact_email': getattr(django_settings, 'EMAIL_CONTACT_TEAM', ''),
        'site_footer': mark_safe(clean_html(settings.footer, full=False)) if settings.footer else None,
        # 'show_cookie_warning': settings.show_cookie_warning,
        'google_analytics': django_settings.GOOGLE_ANALYTICS_ACCOUNT,
        'piwik_server_url': getattr(django_settings,'PIWIK_SERVER_URL', False),
        'assets_version': getattr(django_settings, 'ASSETS_VERSION', 0),
    }

    if with_url:
        url = 'https://%s' % site.domain
        data['site_url'] = url
        data['site_logo'] = url + data['site_logo']
        data['MEDIA_URL'] = '%s%s' % (url, django_settings.MEDIA_URL)

    return data