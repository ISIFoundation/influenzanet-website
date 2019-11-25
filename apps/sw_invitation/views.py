# -*- coding: utf-8 -*-

from .models import Invitation
from django.core.validators import email_re
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.utils.html import strip_tags,escape
from django.utils.encoding import force_unicode
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from apps.sw_invitation.models import InvitationUsage
from .utils import prepare_message, send_message
from . import settings as conf
from apps.sw_auth.models import FakedUser
import re

ACCEPTED_CHARS = re.compile(u'[^-azertyuiopqsdfghjklmwxcvbnéèçàùïâêîôûëö ]', re.UNICODE + re.IGNORECASE)

def render_template(name, request, context=None):
    return render_to_response('sw_invitation/'+name+'.html',
                              context,
                              context_instance=RequestContext(request)
    )

def _is_anonymous(request):
    return not isinstance(request.user, FakedUser)

def clean_text(text):
    text = strip_tags(text)
    text = re.sub(ACCEPTED_CHARS, '', force_unicode(text))
    return text

def parse_form(request):
    emails = request.POST['emails']
    from_name = request.POST['name']
    from_name = escape(clean_text(from_name))
    personnal_text = request.POST['personnal']
    personnal_text = escape(clean_text(personnal_text))
    include_email = int(request.POST.get('include_email', 0))
    if not _is_anonymous(request):
            include_email = int(request.POST.get('include_email', 0))
    else:
            include_email = False

    emails = emails.replace(' ', '')
    emails = emails.split(',')
    e = []
    for email in emails:
        if not email_re.search(email):
            messages.add_message(request, messages.ERROR, _(u'"%s" is not a valid email address') % email)
        else:
            e.append(email)
    return (e, from_name, include_email, personnal_text)

@login_required
def invite(request):
    user = request.user
    # get invitations sent
    invitations = Invitation.objects.all().filter(user=user)
    if invitations.count() > conf.SW_INVITATION_MAX:
        return render_template('max_invitation', request)
    from_name = ''
    if request.method == 'POST':
        emails, from_name, include_email, personnal_text = parse_form(request)
        for email in emails:
                try:
                    key = Invitation.objects.invite(user, email)
                    m = prepare_message(user, key.key, email, include_email, from_name, personnal_text, request.is_secure)
                    send_message(email, m)
                    messages.add_message(request, messages.SUCCESS, _(u'Invitation sent for "%s"') % email)
                except Invitation.AlreadyInvited:
                    messages.add_message(request, messages.ERROR, _(u'email "%s" has already been invited by someone') % email)

    usages = InvitationUsage.objects.filter(user=user).count()
    anonymous = _is_anonymous(request)
    return render_template('invite', request, {'user':user,'from_name':from_name, 'invitations':invitations, 'usages': usages, 'anonymous': anonymous})

@login_required
def preview(request):
    user = request.user
    if request.method == 'POST':
        emails, from_name, include_email, personnal_text = parse_form(request)
        if len(emails) > 0:
            email = emails[0]
        else:
            email = 'dummy@localhost'
        key = Invitation.objects.get_invitation_key(user)
        m = prepare_message(user, key.key, email, include_email, from_name, personnal_text, request.is_secure)
        return render_template('preview', request, {'user':user,'message':m})

