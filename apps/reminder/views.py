from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import base64

from .models import UserReminderInfo, get_upcoming_dates, get_prev_reminder, get_settings, get_default_for_reminder, NewsLetter, NewsletterTracking
from .send import create_message, send, send_unsubscribe_email
from classytags.test.context_managers import NULL

@login_required
def latest_newsletter(request):
    now = datetime.now()
    newsletter_queryset = NewsLetter.objects.filter(date__lte=now, published=True).order_by("-date")
    if newsletter_queryset.count():
        latest_newsletter = newsletter_queryset.all()[0]

        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        language = info.get_language()
        message, outer_message = create_message(request.user, latest_newsletter, language)
        #inner, message = create_message(request.user, latest_newsletter, language)

    return render_to_response('reminder/latest_newsletter.html', locals(), context_instance=RequestContext(request))

def tracking(request, id_tracking):
    tracked, _ = NewsletterTracking.objects.get_or_create(id=id_tracking)
    tracked.tracking+=1
    if not tracked.first_view :
        tracked.first_view=datetime.now()
    tracked.save()
    TRACKING_PIXEL = base64.b64decode( b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')
    PNG_MIME_TYPE = "image/png"

    return HttpResponse(TRACKING_PIXEL, mimetype=PNG_MIME_TYPE)


@login_required
def unsubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        info.active = False
        info.save()

        if get_settings() and get_settings().send_resubscribe_email:
            send_unsubscribe_email(request.user)

        return render_to_response('reminder/unsubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('reminder/unsubscribe.html', locals(), context_instance=RequestContext(request))

@login_required
def resubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        info.active = True
        info.save()
        return render_to_response('reminder/resubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('reminder/resubscribe.html', locals(), context_instance=RequestContext(request))

@staff_member_required
def overview(request):
    upcoming = [{
        'date': d,
        'description': description,
    } for d, description in get_upcoming_dates(datetime.now())]

    return render(request, 'reminder/overview.html', locals())

@staff_member_required
def manage(request, year, month, day, hour, minute):
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])), published=False)
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")

    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    if request.method == "POST":
        sent = True
        send(datetime.now(), request.user, reminder, None, is_test_message=True)

    return render(request, 'reminder/manage.html', locals())

@staff_member_required
def preview(request, year, month, day, hour, minute):
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])), published=False)
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")

    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    text_base, html_content = create_message(request.user, reminder, settings.LANGUAGE_CODE)
    return HttpResponse(html_content)

def _reminder(reminder_dict, user):
    info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True, 'last_reminder': user.date_joined})
    language = info.get_language()

    if not language in reminder_dict:
        language = settings.LANGUAGE_CODE
    if not language in reminder_dict:
        return None

    reminder = reminder_dict[language]

    return reminder
