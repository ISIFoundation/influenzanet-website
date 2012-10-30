# Create your views here.
from django.template import RequestContext, Context
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from apps.survey.models import SurveyUser
from django.contrib import messages
from .models import Token
from apps.sw_cohort.models import CohortUser
from django.contrib.auth.decorators import login_required
from django.db import transaction


def render_template(name, request, context=None):
    return render_to_response('sw_cohort/'+name+'.html',
                              context,
                              context_instance=RequestContext(request)
    )



@login_required
def form(request):
    users = SurveyUser.objects.filter(user=request.user)
    return render_template('form',request, { 'users':users} )

# register a user to a cohort
@login_required
@transaction.commit_manually()
def register(request):
    gid = request.GET.get('gid',None)
    token = request.GET.get('token', None)
    if token is None:
        messages.error(_('token not provided'))
    if gid is None or token is None:
        messages.error('User n')
        return redirect(reverse('cohort_form'))
    cohort = None
    try:
        user = SurveyUser.objects.get(global_id=gid)
        token = Token.objects.get(token=token)
        token.consume()
        subscription = CohortUser()
        subscription.user = user
        subscription.cohort = token.cohort
        subscription.save()
        token.save()
        transaction.commit() 
        cohort = token.cohort
    except Token.DoesNotExist:
        messages.error(_('invalid token'))
        transaction.rollback()
    except Token.TokenException as e:
        messages.error(str(e))
        transaction.rollback()
    return render_template('register', request, {'cohort':cohort })