from datetime import date, datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.sites.models import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required

from apps.common.wait import get_wait_launch_date
from apps.sw_auth.models import EpiworkUser, AnonymizeRequest
from apps.sw_auth.utils import send_activation_email,EpiworkToken, send_user_email
from apps.sw_auth.logger import auth_notify

from .forms import PasswordResetForm, RegistrationForm, SetPasswordForm, UserEmailForm, ReminderSettings,EmailForm

from apps.sw_auth.anonymize import Anonymizer
from django.utils.http import int_to_base36

def render_template(name, request, context=None):
    return render_to_response('sw_auth/'+name+'.html',
                              context,
                              context_instance=RequestContext(request)
    )

def send_email_user_old(user, subject, template, context):
    t = get_template(template)
    send_mail(subject, t.render(Context(context)), None, [user.email])

@csrf_protect
def register_user(request):
    form = None
    if(request.method == "POST"):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            auth_notify('register ok','form is valid')
            d = form.cleaned_data
            user = EpiworkUser.objects.create_user(d['username'], d['email'], d['password1'], d['invitation_key'])
            site = get_current_site(request)
            send_activation_email(user, site)
            return render_template('registration_complete', request, { 'user': user})
    if form is None:
        data = None
        if 'invitation_key' in request.GET:
            data = {'invitation_key': request.GET['invitation_key']}
        form = RegistrationForm(initial=data)
    return render_template('registration_form', request, { 'form': form})


def activate_user(request, activation_key):
    try:
        token = EpiworkToken(activation_key)
        if token.validate(settings.ACCOUNT_ACTIVATION_DAYS):
            user = EpiworkUser.objects.get(token_activate=activation_key, is_active=False)
            user.activate(email_valid=True)
            d = get_wait_launch_date()
            return render_template('activation_complete', request, {'launch_date': d, 'email': user.email, 'login': user.login})
    except:
        pass
    # Nothing found, so it is a fail
    form = UserEmailForm()
    return render_template('activation_failed', request, {'form': form})

@csrf_protect
def activate_retry(request):
    """
    Try another activation
    """
    form = None
    sended = False
    if(request.method == "POST"):
        form = UserEmailForm(request.POST)
        user_found = False
        if form.is_valid():
            users = form.users_cache
            if len(users) > 1:
                user_found = True
                messages.add_message(request, messages.ERROR,_('This email is associated with several accounts. Please contact us to regularize'))
            else:
                if len(users) > 0 :
                    user_found = True
                    user = users[0]
                    if user.is_active == True:
                        messages.add_message(request, messages.INFO,_('The user associated with this email is already activated'))
                    else:
                        try:
                            site = get_current_site(request)
                            send_activation_email(user, site)
                            sended = True
                        except:
                            messages.add_message(request, messages.ERROR, _('Problem occured during activation email generation'))
        if not user_found:
            messages.add_message(request, messages.ERROR,_('This email is not associated with any account'))
    return render_template('activation_retry', request, {'sended': sended, 'form':form})



#@deprecated: Not necessary
def activate_complete(request):
    d = get_wait_launch_date()
    return render_template('activation_complete', request, {'launch_date': d})

@csrf_protect
def password_reset(request):
    form = None
    if(request.method == "POST"):
        form = PasswordResetForm(request.POST)
        if( form.is_valid() ):
            users = form.users_cache
            has_several = len(users) > 1
            if len(users) == 0:
                messages.error(request,_("sorry no corresponding user info was found"))
            else:
                for user in users:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    c = {
                        'has_several': has_several,
                        'username': user.login,
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': site_name,
                        'token': user.create_token_password(),
                        'protocol': request.is_secure() and 'https' or 'http',
                    }

                    send_email_user_old(user, _("Password reset on %s") % site_name, 'sw_auth/password_reset_email.html', c)
            c = {
                'has_several': has_several,
                'count': len(form.users_cache),
                'email': form.cleaned_data['email']
            }
            return render_template('password_reset_done', request, c)
    if form is None:
        form = PasswordResetForm()
    return render_template('password_reset_form', request, {'form': form})

@never_cache
def password_confirm(request, token=None):
    """
    """
    assert token is not None
    form = None
    try:
        tok = EpiworkToken(token)
        if tok.validate(settings.ACCOUNT_ACTIVATION_DAYS):
            user = EpiworkUser.objects.get(token_password=token)
            form = None
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('auth_password_reset_complete'))
            if form is None:
                form = SetPasswordForm(user)
            return render_template('password_reset_confirm', request, {'form': form})
    except:
        pass
    return render_template('password_reset_error', request)


# @deprecated
def password_done(request):
    """
    Nothing to do
    """

def password_complete(request):
    """
    """

def login_token(request, login_token):
    """
    Login using a random key
    """
    next = request.GET.get('next', None)
    if next is None:
        next = settings.LOGIN_REDIRECT_URL

    # Validate the key through the standard Django's authentication mechanism.
    # It also means that the authentication backend of this django-loginurl
    # application has to be added to the authentication backends configuration.
    user = auth.authenticate(login_token=login_token)
    if user is None:
        url = settings.LOGIN_URL
        if next is not None:
            url = '%s?next=%s' % (url, next)
        return HttpResponseRedirect(url)

    # get the token
    token = user._login_token
    del user._login_token # avoid token to propagate
    # The key is valid, then now log the user in.
    auth.login(request, user)

    token.update_usage()

    if token.next is not None:
        next = token.next

    return HttpResponseRedirect(next)


def email_change_confirm(request, user_id, token):
    """
        Confirm the email is valid using a token
    """
    success = True

    tok = EpiworkToken(token)

    try:
        tok.validate(7)
        u = EpiworkUser.objects.get(token_email=token)

        uid = int_to_base36(u.id)
        if not uid == user_id:
            auth_notify('email', "User id doesnt match %s %s " % (user_id, uid))
            success = False
    except Exception, e:
        print e
        success = False

    if not success:
        return render_template('email_change_confirm', request, {'success':False, 'msg': _('Invalid email token') })

    # All is ok change email
    u.use_email_proposal()

    request.session['epiwork_user'] = u # Update the current user in session

    return render_template('email_change_confirm', request, {'success':True, 'u': u })



@login_required
def my_settings(request):
    """
    """
    try:
        epiwork_user = request.session['epiwork_user']
    except KeyError:
        auth_notify('setting', 'No settings')
        return render_template('no_settings', request)

    context = {'epiwork_user': epiwork_user}

    form_reminder = None
    form_email = None
    success = False
    msg = None
    if request.method == "POST":

        action = request.POST.get('action')

        if action == 'settings':
            form_reminder = ReminderSettings(request.POST, instance=request.user)
            if form_reminder.is_valid() :
                form_reminder.save()
                success = True
                msg = _('Your settings have been updated')

        if action == 'email':
            form_email = EmailForm(request.POST, instance=epiwork_user)
            if form_email.is_valid():
                email = form_email.cleaned_data['email']

                token = epiwork_user.create_email_proposal(email)
                user_id = int_to_base36(epiwork_user.id)

                u = reverse('auth_email_change', kwargs={'user_id': user_id, 'token': token})

                url = request.build_absolute_uri( u )

                send_user_email('email_proposal', email, data={'url':url})
                send_user_email('email_proposal_warning', epiwork_user.email, {'email': email})
                msg = _(u'An email has been sent to %(email)s with a link you need to follow to activate this address') % {'email': email }
                success = True

        if action == 'close_account':
            anonymizer = Anonymizer()
            anonymizer.request_close(epiwork_user)
            msg = _(u'The request to close your account has been registered')
            success = True

        if action == 'cancel_close':
            anonymizer = Anonymizer()
            anonymizer.cancel_request(epiwork_user)
            success = True

    if form_reminder is None:
        form_reminder = ReminderSettings(instance=request.user)

    if form_email is None:
        form_email = EmailForm(request.POST, instance=epiwork_user)

    ano = AnonymizeRequest.objects.filter(user=epiwork_user).all()
    if len(ano):
        ano = ano[0]

    context['msg'] = msg
    context['form_reminder'] = form_reminder
    context['form_email'] = form_email
    context['ano_request'] = ano
    context['success'] = success

    return render_template('my_settings', request, context)

@login_required
def deactivate(request, *args):

    confirm = request.GET.get('confirm', default=False)

    if confirm:
        try:
            epiwork_user = request.session['epiwork_user']
            anonymizer = Anonymizer()
            anonymizer.request_close(epiwork_user)
        except KeyError:
            return render_template('no_settings', request)


    return render_template('deactivate_planned', request, {'confirm': confirm})

def index(request):
    """
    """
    return HttpResponseRedirect(reverse('registration_register'))


@staff_member_required
def admin_index(request):
    return render_template('admin/index', request)