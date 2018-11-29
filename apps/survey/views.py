# -*- coding: utf-8 -*-
from datetime import datetime
from urllib import urlencode
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.template import  RequestContext
from django.http import  HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from apps.common.wait import is_wait_launch, get_wait_launch_context

from apps.survey import utils, models, forms
from apps.survey.household import SurveyHousehold

import apps.pollster as pollster

from apps.grippenet.cohorts import get_survey_user_channel, get_cohort_users
from apps.grippenet.models import PregnantCohort
from django.template.base import TemplateDoesNotExist

def _get_avatars(with_list=True):

    """
    Return the avatar configuration if activated, None otherwise
    list :list of available avatars (list of the file number in the SURVEY_AVATARS directory (subdirectory of media)
    An avatar is just a 32x32 png image
    url: url to the avatar dir
    """

    SURVEY_AVATARS = getattr(settings, 'SURVEY_AVATARS', None)

    ## Path to the avatars files, relative to media directory
    if not SURVEY_AVATARS:
        return None
    url = settings.MEDIA_URL + '/' + SURVEY_AVATARS.strip('/') + '/'
    if with_list:
        try:
            from .avatars import AVATARS
        except:
            AVATARS = None
        conf = None
        if AVATARS:
            conf = {'list': AVATARS, 'url': url }
    else:
        # list not request, return only url
        conf = {'url': url}
    return conf

def get_active_survey_user(request):
    gid = request.GET.get('gid', None)
    if gid is None:
        return None
    else:
        try:
            return models.SurveyUser.objects.get(global_id=gid,
                                                 user=request.user)
        except models.SurveyUser.DoesNotExist:
            raise ValueError()

def _get_all_health_status():
    return  {
        "NO-SYMPTOMS":                                  _('No symptoms'),
        "ILI":                                          _('Flu symptoms'),
        "COMMON-COLD":                                  _('Common cold'),
        "GASTROINTESTINAL":                             _('Gastrointestinal symptoms'),
        "ALLERGY-or-HAY-FEVER-and-GASTROINTESTINAL":    _('Allergy / hay fever and gastrointestinal symptoms'),
        "ALLERGY-or-HAY-FEVER":                         _('Allergy / hay fever'),
        "COMMON-COLD-and-GASTROINTESTINAL":             _('Common cold and gastrointestinal symptoms'),
        "NON-SPECIFIC-SYMPTOMS":                        _('Other non-influenza symptons'),
    }

def _decode_person_health_status(status):
    d = _get_all_health_status()
    if status in d:
        return d[status]
    return _('Unknown')

def _get_person_health_status(request, survey, global_id):
    data = survey.get_last_participation_data(request.user.id, global_id)
    status = None
    if data:
        cursor = connection.cursor()
        params = { 'weekly_id': data["id"] }
        queries = {
            'sqlite':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = :weekly_id""",
            'mysql':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = :weekly_id""",
            'postgresql':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = %(weekly_id)s"""
        }
        cursor.execute(queries[utils.get_db_type(connection)], params)
        result = cursor.fetchone()
        status = result[0] if result else None
    return (status, _decode_person_health_status(status))

def _get_health_history(request, survey, table="pollster_results_weekly", limit=None):
    results = []
    cursor = connection.cursor()
    params = { 'user_id': request.user.id }
    queries = {
        'sqlite':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, """ + table + """ W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = :user_id
             ORDER BY W.timestamp DESC""",
        'mysql':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, """ + table + """ W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = :user_id
             ORDER BY W.timestamp DESC""",
        'postgresql':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, """ + table + """ W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = %(user_id)s
             ORDER BY W.timestamp DESC""",
    }
    query = queries[utils.get_db_type(connection)]
    if limit is not None:
        query += " LIMIT " + str(limit)
    cursor.execute(query, params)

    results = cursor.fetchall()
    cursor.close()
    participants = {}
    for ret in results:
        timestamp, global_id, status = ret
        survey_user = participants.get(global_id)
        if survey_user is None:
            survey_user = models.SurveyUser.objects.get(global_id=global_id)
            participants[global_id] = survey_user
        yield {'global_id': global_id, 'timestamp': timestamp, 'status': status, 'diag':_decode_person_health_status(status), 'survey_user': survey_user}

def _get_group_last_survey(request, survey):
    cursor = connection.cursor()
    params = { 'user_id': request.user.id }
    queries = {
        'sqlite':"SELECT MAX(W.timestamp), W.global_id FROM pollster_results_" + survey + " W WHERE W.user = :user_id GROUP BY W.global_id",
        'mysql': "SELECT MAX(W.timestamp), W.global_id FROM pollster_results_" + survey + " W WHERE W.user = :user_id GROUP BY W.global_id",
        'postgresql':"SELECT MAX(W.timestamp), W.global_id FROM pollster_results_" + survey + " W WHERE W.user =  %(user_id)s GROUP BY W.global_id",
    }
    cursor.execute(queries[utils.get_db_type(connection)], params)
    data = cursor.fetchall()
    cursor.close()
    results = {}
    for d in data:
        timestamp, global_id = d
        results[global_id] = timestamp
    return results

def _get_group_vaccination(request):
    try:
        cursor = connection.cursor()
        #params = { 'user_id':  }
        query = "SELECT s.global_id from vaccination_surveyuser v left join survey_surveyuser s on v.surveyuser_id=s.id where s.user_id= %d" % request.user.id
        cursor.execute(query)
        results = cursor.fetchall()
        return [r[0] for r in results]
    except:
        return []

def create_survey_user(request):
    su = models.SurveyUser.objects.create_survey_user(request.user)
    h = SurveyHousehold.get_household(request)
    h.participants_updated(request)
    return su


@login_required
def wait_launch(request):
    h = SurveyHousehold.get_household(request)
    avatars = _get_avatars(with_list=False)
    wait_launch = get_wait_launch_context(request)
    return render_to_response('survey/wait_launch.html', {'wait': wait_launch, 'household': h, 'avatars': avatars}, context_instance=RequestContext(request))

@login_required
def group_management(request):

    if is_wait_launch(request):
        return HttpResponseRedirect(reverse('survey_wait_launch'))
    try:
        survey = pollster.models.Survey.get_by_shortname('weekly')
        survey.set_caching(getattr(settings, 'POLLSTER_USE_CACHE', False))
    except:
        raise Exception("The survey application requires a published survey with the shortname 'weekly'")
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass

    household = SurveyHousehold.get_household(request)

    if request.method == "POST":
        global_ids = request.POST.getlist('global_ids')

        action = request.POST.get('action')

        if action == 'healthy':
            Weekly = survey.as_model()

        update_household = False

        for (gid, survey_user) in household.participants.items():
            if not gid in global_ids:
                continue

            if action == 'healthy':

                profile = household.get_simple_profile(gid)
                if not profile:
                    messages.add_message(request, messages.ERROR,
                        _(u'Please complete the background questionnaire for the participant "%(user_name)s" before marking him/her as healthy.') % {'user_name': survey_user.name})
                    continue

                channel = get_survey_user_channel(survey_user)

                Weekly.objects.create(
                    user=request.user.id,
                    global_id=survey_user.global_id,
                    channel=channel,
                    Q1_0=True, # Q1_0 => "No symptoms. The other fields are assumed to have the correct default information in them.
                    timestamp=datetime.now(),
                )
                messages.add_message(request, messages.INFO, _(u'The participant "%(user_name)s" has been marked as healthy.') % {'user_name': survey_user.name})

            elif action == 'delete':
                survey_user.deleted = True
                update_household = True
                survey_user.save()

            if update_household:
                household.participants_updated(request)

    last_intakes = _get_group_last_survey(request, 'intake')
    last_weeklies = _get_group_last_survey(request, 'weekly')

    #vacc2017 = _get_group_last_survey(request, 'vacc2017')

    persons = models.SurveyUser.objects.filter(user=request.user, deleted=False)

    cohorts = get_cohort_users(persons)

    active_cohorts = {}
    for person in persons:
        # person.health_status, person.diag = _get_person_health_status(request, survey, person.global_id)
        # person.health_history = [i for i in history if i['global_id'] == person.global_id][:10]
        person.last_weekly = last_weeklies.get(person.global_id)
        person.last_intake = last_intakes.get(person.global_id)
        for cohort_id, subscribers in cohorts.items():
            p = subscribers.get(str(person.id))
            if p is not None:
                active_cohorts[cohort_id] = True
            setattr(person, cohort_id, p)

    template = getattr(settings, 'SURVEY_GROUP_TEMPLATE', 'group_management')

    wait_launch = get_wait_launch_context(request) # is request restricted by wait_launch context

    avatars = _get_avatars(with_list=False)

    active_cohorts = active_cohorts.keys()

    ctx = {
          # 'vacc2017': vacc2017,
          # 'has_vacc2017': len(vacc2017) > 0,
           'persons': persons,
           'gid': request.GET.get("gid"),
           'wait_launch':wait_launch,
           'avatars': avatars,
           'cohorts': active_cohorts,
           }

    return render_to_response('survey/'+template+'.html', ctx, context_instance=RequestContext(request))

@login_required
def thanks_profile(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass

    household = SurveyHousehold.get_household(request)
    return render_to_response('survey/thanks_profile_sw.html', {'person': survey_user,'household':household, 'avatars': _get_avatars(with_list=False) },
        context_instance=RequestContext(request))

@login_required
def select_user(request, template='survey/select_user.html'):
    # @todo: more generic select_user that can hold some extra url parameters
    next = request.GET.get('next', None)

    if next is None:
        next = reverse('survey_index')

    users = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    total = len(users)
    survey_user = None

    if total == 0:
        survey_user = create_survey_user(request)

    elif total == 1:
        survey_user = users[0]

    if survey_user is not None:
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)

    return render_to_response(template, {
        'users': users,
        'next': next,
        'avatars': _get_avatars(with_list=False)
    }, context_instance=RequestContext(request))


def redirect_to_survey(request, shortname):
    url = reverse('survey_fill', kwargs={'shortname': shortname })
    query = {}
    for v in ['next','gid']:
        p = request.GET.get(v, None)
        if p is not None:
            query[v] = p
    if len(query) > 0:
        url = url + '?' + urlencode(query)
    return HttpResponseRedirect( url )

@login_required
def index(request):
    return redirect_to_survey(request, 'weekly')

@login_required
def profile_index(request):
    return redirect_to_survey(request, 'intake')

@login_required
def create_surveyuser(request):
    if is_wait_launch(request):
        return HttpResponseRedirect(reverse('survey_wait_launch'))

    if models.SurveyUser.objects.filter(user=request.user, deleted=False).count() > 1:
        return HttpResponseRedirect(reverse(group_management))

    if models.SurveyUser.objects.filter(user=request.user, deleted=False).count() == 0:
        survey_user = create_survey_user(request)

    gid = models.SurveyUser.objects.get(user=request.user, deleted=False).global_id
    return HttpResponseRedirect(reverse('survey_index') + '?gid=' + gid)

@login_required
def run_index(request, shortname):
    return redirect_to_survey(request, shortname)

@login_required
def run_survey(request, shortname):
    if is_wait_launch(request, shortname):
        return HttpResponseRedirect(reverse('survey_wait_launch'))

    # Check of survey user is done here
    # Because it's survey app responsability to manage the SurveyUser and create if if necessary
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        # TODO allow query params forwarding (or save it in session)
        url = '%s?next=%s' % (reverse("survey_select_user"), reverse("survey_fill", kwargs={'shortname':shortname}))
        return HttpResponseRedirect(url)

    from apps.pollster.runner import SurveyRunner
    runner = SurveyRunner()
    return runner.run(request, survey_user, shortname)

@login_required
def thanks_run(request, shortname):
    survey_user = None
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass

    data = {'person': survey_user}
    ctx = RequestContext(request)

    try:
        response = render_to_response('survey/thanks_'+ shortname +'.html', data, context_instance=ctx)
    except TemplateDoesNotExist:
        response = render_to_response('survey/thanks_base.html', data, context_instance=ctx)
    return response

@login_required
def people_edit(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(people_edit))
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    current_avatar = survey_user.avatar
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user.name = form.cleaned_data['name']
            survey_user.avatar = form.cleaned_data['avatar']
            survey_user.save()

            h = SurveyHousehold.get_household(request)
            h.participants_updated(request)

            return HttpResponseRedirect(reverse(group_management))

    else:
        form = forms.AddPeople(initial={'name': survey_user.name})

    return render_to_response('survey/people_edit.html', {'form': form, 'avatars': _get_avatars(), 'current_avatar': current_avatar ,'survey_user':survey_user},
                              context_instance=RequestContext(request))

@login_required
def people_remove(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = reverse(group_management)
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    confirmed = request.POST.get('confirmed', None)

    if confirmed is not None:
        if confirmed == 'Y':
            survey_user.remove()

            h = SurveyHousehold.get_household(request)
            h.participants_updated(request)

        elif confirmed == 'N':
            url = reverse(group_management)
        return HttpResponseRedirect(reverse(group_management))

    return render_to_response('survey/people_remove.html', {'person': survey_user},
                              context_instance=RequestContext(request))

@login_required
def people_add(request):
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user = models.SurveyUser()
            survey_user.user = request.user
            survey_user.name = form.cleaned_data['name']
            survey_user.avatar = form.cleaned_data['avatar']
            survey_user.save()

            h = SurveyHousehold.get_household(request)
            h.participants_updated(request)

            messages.add_message(request, messages.INFO,
                _('A new person has been added.'))

            next = request.GET.get('next', None)
            if next is None:
                url = reverse(group_management)
            else:
                url = '%s?gid=%s' % (next, survey_user.global_id)
            return HttpResponseRedirect(url)

    else:
        form = forms.AddPeople()

    return render_to_response('survey/people_add.html', {'form': form,'avatars': _get_avatars(), 'current_avatar': 0},
                              context_instance=RequestContext(request))


