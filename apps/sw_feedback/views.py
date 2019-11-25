# -*- coding: utf-8 -*-

from .forms import *
from django.shortcuts import render_to_response, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template import RequestContext
from .feedback import feeback_token

from apps.pollster.models import Chart

def feedback(request):
    page = request.GET.get('from', '')
    try:
        site_token = settings.SW_FEEDBACK_SITE
    except:
        raise Exception('Feedback application not configured')

    r = feeback_token(site_token)
    try:
        token = r['token']
    except:
        token = None
    return render_to_response('sw_feedback/feedback.html',{ 'token':token, 'page': page })

def tell_a_friend(request):
    if request.method == 'POST':
        form = TellAFriendForm(request.POST)
        form.initCaptcha(request.session['captcha'])
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']

            message = "Bonjour,\n\nUn ami vous conseille le site GrippeNet.fr.\nVous pouvez visiter le site à l'adresse https://www.grippenet.fr.\n\nL'équipe GrippeNet.fr"

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email] )

            return render_to_response('sw_feedback/sent.html', RequestContext(request, { email: email }))
    else:
        form = TellAFriendForm()
    value = form.updateCaptcha()
    #print 'session %d' % value
    request.session['captcha'] = value
    return render_to_response('sw_feedback/tell_a_friend.html',RequestContext(request, {
        'form': form,
    }))

def maps(request):
    charts = Chart.objects.all() # filter(status='PUBLISHED')
    chart_id = request.GET.get('chart',None)
    if( not chart_id is None ):
        chart = Chart.objects.get(shortname=chart_id)
    else:
        chart = None
    return render_to_response('sw_feedback/maps.html',
                              RequestContext(request, {
                                'charts': charts,
                                'chart_id':chart_id,
                                'chart':chart
                                }
                               ))