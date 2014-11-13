from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.conf import settings as django_settings
from cms.utils.html import clean_html

from .models import SiteSettings

def customizations(request):
    return site_context()

def site_context():
    site = Site.objects.get_current()
    settings = SiteSettings.get(site)

    return {
        'site_name': site.name,
        'site_logo': settings.logo.url if settings.logo else "",
        'site_footer': mark_safe(clean_html(settings.footer, full=False)) if settings.footer else None,
        # 'show_cookie_warning': settings.show_cookie_warning,
        'google_analytics': django_settings.GOOGLE_ANALYTICS_ACCOUNT,
        'piwik_server_url': getattr(django_settings,'PIWIK_SERVER_URL', False),
    }
