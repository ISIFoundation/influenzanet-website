import datetime
import smtplib
from traceback import format_exc

from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Context, loader, Template
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.translation import activate

import loginurl.utils
from apps.partnersites.context_processors import site_context

from .models import get_reminders_for_users, UserReminderInfo, ReminderError, get_settings

def create_message(user, message, language, next=None, tracker=None):
    if language:
        activate(language)

    t = Template(message.message)
    c = {
        'url': get_url(user, next),
        'unsubscribe_url': get_login_url(user, reverse('apps.reminder.views.unsubscribe')),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }
    c.update(site_context())
    c['site_logo'] = get_site_url() + c['site_logo']
    c['site_url'] = get_site_url()
    inner = t.render(Context(c))
    template = 'reminder/message.html'

    if message.html_template is not None and message.html_template != "":
        template = message.html_template
    t = loader.get_template(template)
    c['inner'] = inner
    c['MEDIA_URL'] = get_media_url()
    c['message'] = message
    c['tracking_url'] =get_tracking_url(tracker)
    return inner, t.render(Context(c))

def send_reminders(fake=False):
    now = datetime.datetime.now()
    print "now=%s" % str(now)
    i = -1
    for i, (user, message, language) in enumerate(get_reminders_for_users(now, User.objects.filter(is_active=True))):
        if not fake:
            send(now, user, message, language)
        else:
            print 'sending', user.email, message.subject

    return i + 1

#A modifier




def get_site_url():
    return 'https://%s' % Site.objects.get_current().domain

def get_media_url():
    return '%s%s' % (get_site_url(), settings.MEDIA_URL)

def get_url(user, next):
    if next is None:
        next = get_survey_url()
    return get_login_url(user, next)

def get_login_url(user, next):
    expires = datetime.datetime.now() + datetime.timedelta(days=30)

    usage_left = 5
    key = loginurl.utils.create(user, usage_left, expires, next)

    domain = Site.objects.get_current()
    path = reverse('loginurl-index').strip('/')
    loginurl_base = 'https://%s/%s' % (domain, path)

    return '%s/%s' % (loginurl_base, key.key)

def get_tracking_url(tracker) :
    domain = Site.objects.get_current()
    path=reverse('tracking', args=[tracker.id])
    #'https://%s' % Site.objects.get_current().domain
    return 'http://%s%s' % (domain,path)

def get_survey_url():
    domain = Site.objects.get_current()
    path = reverse('survey_index')
    return 'https://%s%s' % (domain, path)

def send(now, user, message, language, is_test_message=False, next=None, headers=None, tracker=None):
    text_base, html_content = create_message(user, message, language, next, tracker)
    text_content = strip_tags(text_base)

    msg = EmailMultiAlternatives(
        message.subject,
        text_content,
        "%s <%s>" % (message.sender_name, message.sender_email),
        [user.email],
        headers=headers,
    )

    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except Exception, e:
        ReminderError.objects.create(
            user=user,
            message=unicode(e),
            traceback=format_exc(),
        )
    if not is_test_message:
        info = UserReminderInfo.objects.get(user=user)
        info.last_reminder = now
        info.save()
        return(headers)

def send_unsubscribe_email(user):
    reminder_settings = get_settings()

    t = Template(reminder_settings.resubscribe_email_message)
    c = {
        'url': get_url(user),
        'resubscribe_url': get_login_url(user, reverse('apps.reminder.views.resubscribe')),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
    }
    c.update(site_context())
    c['site_logo'] = get_site_url() + c['site_logo']
    inner = t.render(Context(c))

    t = loader.get_template('reminder/message.html')
    c['inner'] = inner
    c['MEDIA_URL'] = get_media_url()
    c['message'] = {'date': {"date": datetime.date.today()}} # this is the only part of message that's used in message.html

    html_content = t.render(Context(c))

    text_content = strip_tags(inner)

    msg = EmailMultiAlternatives(
        reminder_settings.resubscribe_email_message,
        text_content,
        None,
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
