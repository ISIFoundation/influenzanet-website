# -*- coding: utf-8 -*-
from django.core.urlresolvers import get_resolver, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.utils.safestring import mark_safe
from django.utils.translation import to_locale, get_language, ugettext as _
from django.utils import simplejson
from django.template import RequestContext

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.conf import settings

from cms import settings as cms_settings
from apps.survey.models import SurveyUser
from .utils import get_user_profile
from . import models, forms, fields, parser, json
import re, datetime, locale, csv, urlparse, urllib

def request_render_to_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def retry(f, *args, **kwargs):
    tries = 2
    while tries:
        try:
            return f(*args, **kwargs)
        except:
            tries -= 1
            if tries == 0:
                raise

@staff_member_required
def survey_list(request):
    surveys = models.Survey.objects.all()
    form_import = forms.SurveyImportForm()
    return request_render_to_response(request, 'pollster/survey_list.html', {
        "surveys": surveys,
        "form_import": form_import
    })

@staff_member_required
def survey_add(request):
    survey = models.Survey()
    if (request.method == 'POST'):
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            # create and redirect
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    # return an empty survey structure
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return request_render_to_response(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": cms_settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_edit(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if not survey.is_editable:
        return redirect(survey_test, id=id)
    if request.method == 'POST':
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return request_render_to_response(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": cms_settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_publish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        errors = survey.publish()
        if errors:
            messages.error(request, 'Unable to publish the survey, please check the errors below')
            for error in errors[:5]:
                messages.warning(request, error)
        return redirect(survey)
    return redirect(survey)

@staff_member_required
def survey_unpublish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        survey.unpublish()
        return redirect(survey)
    return redirect(survey)

@staff_member_required
def survey_test(request, id, language=None):
    survey = get_object_or_404(models.Survey, pk=id)
    if language:
        translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
        survey.set_translation_survey(translation)
    if language is None:
        language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"
    # survey_user = _get_active_survey_user(request)
    # user = _get_active_survey_user(request)
    form = None
    # user_id = request.user.id
    # global_id = survey_user and survey_user.global_id
    last_participation_data = None

    # In test env, do not get the user_id from global_id
    # to allow test with real data (for debugging)
    global_id = request.GET.get('gid')
    force_previous = request.GET.get('previous', False)
    user_id = None
    if global_id:
        try:
            survey_user = SurveyUser.objects.get(global_id=global_id)
            user_id = survey_user.user.id
            if force_previous:
                last_participation_data = models.previous_season_data(survey.shortname, user_id, global_id)
            else:
                last_participation_data = survey.get_prefill_data(user_id, global_id)
        except SurveyUser.DoesNotExist:
            pass


    post_data = None

    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = user_id
        data['global_id'] = global_id
        data['timestamp'] = datetime.datetime.now()
        form = survey.as_form()(data)
        if form.is_valid():
           post_data = data
        else:
            survey.set_form(form)
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_participation_data_json = encoder.encode(last_participation_data)

    return request_render_to_response(request, 'pollster/survey_test.html', {
        "language": language,
        "locale_code": locale_code,
        "survey": survey,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "last_participation_data_json": last_participation_data_json,
        "language": language,
        "form": form,
        "post_data": post_data,
    })

def survey_run(request, shortname, next=None, clean_template=False):
    from apps.survey.views import _get_person_health_status

    if 'login_key' in request.GET:
        user = authenticate(key=request.GET['login_key'])
        if user is not None:
            login(request, user)

        # deal with the else branch somehow, since it's rather unexpected to have login_key in the
        # GET, yet have it be incorrect?

    # @login_required from this point on.
    if not request.user.is_authenticated():
        if clean_template: # i.e. "if is_mobile"
            return HttpResponse(simplejson.dumps({'error': True, 'error_code': 3, 'error_msg': 'you must be logged in'}), mimetype="application/json")
        return redirect_to_login(request.path)

    use_cache = getattr(settings, 'POLLSTER_USE_CACHE', False)
    survey = get_object_or_404(models.Survey, shortname=shortname, status='PUBLISHED')
    if use_cache:
        survey.set_caching(True)
    language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"
    translation = get_object_or_none(models.TranslationSurvey, survey=survey, language=language, status="PUBLISHED")
    if translation is not None:
        if use_cache:
            translation.prefetch_tranlations()
        survey.set_translation_survey(translation)
    survey_user = _get_active_survey_user(request)
    form = None
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    last_participation_data = survey.get_prefill_data(user_id, global_id)

    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = user_id
        data['global_id'] = global_id
        data['timestamp'] = datetime.datetime.now()
        form = survey.as_form()(data)
        if form.is_valid():
            form.save()
            next_url = next or _get_next_url(request, reverse("survey_run", kwargs={'shortname': shortname}))
            if global_id:
                # add or override the 'gid' query parameter
                next_url_parts = list(urlparse.urlparse(next_url))
                query = dict(urlparse.parse_qsl(next_url_parts[4]))
                query.update({'gid': global_id})
                next_url_parts[4] = urllib.urlencode(query)
                next_url = urlparse.urlunparse(next_url_parts)

            if survey.shortname == 'weekly':
                __, diagnosis = _get_person_health_status(request, survey, global_id)
                messages.info(request, _("Thanks - your diagnosis:") + u" " + u"%s" % diagnosis)
            else:
                messages.info(request, _("Thanks for taking the time to fill out this survey."))

            return HttpResponseRedirect(next_url)
        else:
            survey.set_form(form)
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_participation_data_json = encoder.encode(last_participation_data)

    timestamp_last_fill = None
    pollster_debug = request.GET.get('pollster_debug', False)
    if last_participation_data:
        # check if the data are from previous year
        data_source = last_participation_data.get('_source_','')
        if data_source == 'previousdata':
            messages.info(request, _("At the beginning of the season we ask you to verify last year's information. Please check the information below."))
        else:
            # Previous filling timestamp
            timestamp_last_fill = last_participation_data.get('timestamp', None)

    return request_render_to_response(request, "pollster/survey_run_clean.html" if clean_template else 'pollster/survey_run.html', {
        "language": language,
        "locale_code": locale_code,
        "survey": survey,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "timestamp_last_fill": timestamp_last_fill,
        "last_participation_data_json": last_participation_data_json,
        "form": form,
        "person": survey_user,
        "pollster_debug": pollster_debug,
    })

def survey_map(request, survey_shortname, chart_shortname):
    survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
    chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)

    global_id = request.GET.get('gid', None)
    profile = None
    if global_id:
        profile = get_user_profile(request.user.id, global_id)

    return request_render_to_response(request, 'pollster/mobile_survey_chart.html', {
        'profile': profile,
        'chart': chart,
    })

@staff_member_required
def survey_translation_list_or_add(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyTranslationAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyTranslationAddForm(request.POST)
        if form_add.is_valid():
            language = form_add.cleaned_data['language']
            translations = survey.translationsurvey_set.all().filter(language=language)[0:1]
            if translations:
                translation = translations[0]
            else:
                translation = models.TranslationSurvey(survey=survey, language=language)
                survey.set_translation_survey(translation)
                survey.translation_survey.save()
                for question in survey.questions:
                    question.translation_question.save()
                    for option in question.options:
                        option.translation_option.save()
                    for row in question.rows:
                        row.translation_row.save()
                    for column in question.columns:
                        column.translation_column.save()
            return redirect(translation)
    return request_render_to_response(request, 'pollster/survey_translation_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_translation_edit(request, id, language):
    survey = get_object_or_404(models.Survey, pk=id)
    translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
    survey.set_translation_survey(translation)
    if request.method == 'POST':
        forms = []
        forms.append( survey.translation.as_form(request.POST) )
        for question in survey.questions:
            forms.append( question.translation.as_form(request.POST) )
            for row in question.rows:
                forms.append( row.translation.as_form(request.POST) )
            for column in question.columns:
                forms.append( column.translation.as_form(request.POST) )
            for option in question.options:
                forms.append( option.translation.as_form(request.POST) )
        if all(f.is_valid() for f in forms):
            for form in forms:
                form.save()
            messages.success(request, 'Translation saved successfully.')
            return redirect(translation)
    return request_render_to_response(request, 'pollster/survey_translation_edit.html', {
        "survey": survey,
        "translation": translation
    })

@staff_member_required
def survey_chart_list_or_add(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyChartAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyChartAddForm(request.POST)
        if form_add.is_valid():
            shortname = form_add.cleaned_data['shortname']
            charts = survey.chart_set.all().filter(shortname=shortname)[0:1]
            if charts:
                chart = charts[0]
            else:
                chart = models.Chart(survey=survey, shortname=shortname)
                chart.type = models.ChartType.objects.all().order_by('id')[0]
                chart.save()
            return redirect(chart)
    return request_render_to_response(request, 'pollster/survey_chart_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_chart_edit(request, id, shortname):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    form_chart = forms.SurveyChartEditForm(instance=chart)
    if request.method == 'POST':
        form_chart = forms.SurveyChartEditForm(request.POST, instance=chart)
        if form_chart.is_valid():
            form_chart.save()
            if not chart.update_table():
                msg = 'Unable to gather some data. Please check the SQL statements.'
                if chart.is_published:
                    messages.error(request, msg)
                else:
                    messages.warning(request, msg)
            return redirect(chart)
    if chart.is_template:
        # Note that this is just the rendering of a preview, so _any_ survey
        # user is enough to render it, that's why we use _get_some_survey_user().
        survey_user = _get_active_survey_user(request)
        if survey_user is None:
            survey_user = _get_first_survey_user(request)
        global_id = survey_user and survey_user.global_id
        user_id = request.user.id
        profile = None
        if global_id:
            profile = get_user_profile(user_id, global_id)
        context = RequestContext(request, {
            'user_id': user_id,
            'global_id': global_id,
            'profile': profile,
            'chart': chart
        })
        try:
            preview = chart.render(context)
        except Exception, e:
            preview = "An error occurred during chart preview:\n" + str(e)
    else:
        preview = None
    return request_render_to_response(request, 'pollster/survey_chart_edit.html', {
        "survey": survey,
        "chart": chart,
        "preview": preview,
        "form_chart": form_chart
    })

@staff_member_required
def survey_chart_data(request, id, shortname):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

@staff_member_required
def survey_chart_map_tile(request, id, shortname, z, x, y):
    if int(z) > 22:
        raise Http404
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

@staff_member_required
def survey_chart_map_click(request, id, shortname, lat, lng):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

@staff_member_required
def survey_results_csv(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    now = datetime.datetime.now()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=survey-results-%d-%s.csv' % (survey.id, format(now, '%Y%m%d%H%M'))
    writer = csv.writer(response)
    survey.write_csv(writer)
    return response

@staff_member_required
def survey_export_xml(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    now = datetime.datetime.now()
    response = render(request, 'pollster/survey_export.xml', { "survey": survey }, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=survey-export-%d-%s.xml' % (survey.id, format(now, '%Y%m%d%H%M'))
    return response

@staff_member_required
def survey_import(request):
    form_import = forms.SurveyImportForm()
    if request.method == 'POST':
        form_import = forms.SurveyImportForm(request.POST, request.FILES)
        if form_import.is_valid():
            xml = request.FILES['data'].read()
            survey = models.Survey()
            # create and redirect
            parser.survey_update_from_xml(survey, xml)
            return redirect(survey)
    return redirect(survey_list)

def chart_data(request, survey_shortname, chart_shortname):
    chart = None

    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')

    survey_user = _get_active_survey_user(request)
    if survey_user is None:
        survey_user = _get_first_survey_user(request)

    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

def map_tile(request, survey_shortname, chart_shortname, z, x, y):
    if int(z) > 22:
        raise Http404
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

def map_click(request, survey_shortname, chart_shortname, lat, lng):
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

# based on http://djangosnippets.org/snippets/2059/

def urls(request, prefix=''):
    """
        Returns javascript for mapping service endpoint names to urls.

        For this view to work properly, all urls that are to be made
        available and are using regular expressions for defining
        parameters must use named parameters.

        The view uses Django internal url resolver to iterate over a list
        of all currently defined url patterns.  It looks for named patterns
        and replaces each named regex group definition the group name enclosed
        in curley braces.  Url pattern names will be translated into
        javascript variable names by converting all letters to the upper
        case and replacing '-' with '_'.
        """
    resolver = get_resolver(None)

    urls = {}

    for name in resolver.reverse_dict:
        if isinstance(name, str) and name.startswith(prefix):
            url_regex = resolver.reverse_dict.get(name)[1]
            param_names = resolver.reverse_dict.get(name)[0][0][1]
            arg_pattern = r'\(\?P\<[^\)]+\)'  #matches named groups in the form of (?P<name>pattern)

            i = 0
            for match in re.findall(arg_pattern, url_regex):
                url_regex = url_regex.replace(match, "{%s}"%param_names[i])
                i += 1

            urls[name] = "/" + url_regex[:-1]

    return request_render_to_response(request, "pollster/urls.js", {'urls':urls}, mimetype="application/javascript")

def _get_active_survey_user(request):
    gid = request.GET.get('gid', None)
    if gid is None or not request.user.is_active:
        return None
    else:
        return get_object_or_404(SurveyUser, global_id=gid, user=request.user)

def _get_first_survey_user(request):
    # As remarked in other locations, the passing of the gid is not a robust
    # way of doing things. This helper method is used if no gid is available
    # to get at least some survey user if there is any available survey user.

    if not request.user.is_authenticated():
        return None

    survey_users = SurveyUser.objects.filter(user=request.user, deleted=False).order_by("id")

    if len(survey_users) >= 1:
        return survey_users[0]

    return None

def _get_next_url(request, default):
    url = request.GET.get('next', default)
    survey_user = _get_active_survey_user(request)
    if survey_user:
        url = '%s?gid=%s' % (url, survey_user.global_id)
    return url

