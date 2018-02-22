from django import template
import datetime
from django.utils.translation import ungettext, ugettext

register = template.Library()

SECS_IN_DAY = 3600 * 24

def delay_str(single, plural, count):
    type = ungettext(single, plural, count)
    return ugettext('%(count)d %(type)s') % {'count': count, 'type': type }

def time_to_delay(d):
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    now = datetime.datetime.now()
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds

    print since
    if since < 0:
        return u'0 ' + ugettext('minute')
    if since < 3600:
        n = since // 60
        return delay_str('minute', 'minutes', n)
    if since < (3600 * 24):
        n = since // 3600
        return delay_str('hour', 'hours', n)
    if since < (3600 * 24 * 7):
        n = since // SECS_IN_DAY
        return delay_str('day', 'days', n)
    if since < (3600 * 24 * 30):
        n = since // (3600 * 24 * 7)
        return delay_str('week', 'weeks', n)
    if since < (3600 * 24 * 365):
        n = since // (3600 * 24 * 30)
        return delay_str('month', 'months', n)
    n = since // (3600 * 24 * 365)
    return delay_str('year', 'years', n)

@register.filter(name="survey_timesince")
def timesince(value):
    if not value:
        return u''
    try:
        return time_to_delay(value)
    except (ValueError, TypeError):
        return u''
timesince.is_safe = False
