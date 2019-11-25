from django.conf import settings
from django.core import exceptions
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import get_language
from django.utils.log import getLogger

import datetime, urlparse, urllib

from apps.common.importlib import load_class_from_path
from apps.common.db import quote_query, get_cursor
from apps.common.i18n import get_locale

from . import models, views, json, fields
from django.core.urlresolvers import reverse

CONFIG =  getattr(settings, 'POLLSTER_RUNNER', None)
if CONFIG is None:
    raise exceptions.ImproperlyConfigured('SurveyRunner is not configured')

if not CONFIG.has_key('workflows'):
    raise exceptions.ImproperlyConfigured('Missing workflows in pollster runner')

WORKFLOWS = []
WORKFLOWS_LOADED = False

def get_workflows():
    global WORKFLOWS
    global WORKFLOWS_LOADED
    if not WORKFLOWS_LOADED:
        # print 'loading'
        for path in CONFIG['workflows']:
            w = load_class_from_path(path)
            WORKFLOWS.append(w)
        WORKFLOWS_LOADED = True
    return WORKFLOWS

logger = getLogger('pollster.runner')

DEBUG = settings.DEBUG

def as_json(data):
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    return encoder.encode(data)

def update_url_params(url, params):
    """
        Update url params with new params
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    url = urlparse.urlunparse(url_parts)
    return url

class BaseWorkflow(object):

    def debug(self, message):
        logger.debug(message)

    def user_has_data(self, shortname, survey_user):
        """
            Check if a given user has data for a survey

        """
        # Here use a direct query to avoid the load of all the survey in order to
        # build the model
        # A static method in Survey class would be the best for it
        survey = models.Survey.get_by_shortname(shortname)
        if survey is None:
            raise models.Survey.DoesNotExist()
        # @todo get this directly using an dedicated method of Survey
        table = "pollster_"  + survey.get_table_name()
        query = "select {{timestamp}} from {{" + table +"}} WHERE {{user}}=%s AND {{global_id}}=%s LIMIT 1"
        query = quote_query(query)
        cursor = get_cursor()
        cursor.execute(query, [ survey_user.user.id, survey_user.global_id ])
        r = cursor.fetchone()
        if r is not None:
            return True
        return False

    def user_get_last_data(self, shortname, survey_user):
        """
        Returns the last available response of a survey
        """
        survey = models.Survey.get_by_shortname(shortname)
        if survey is None:
            raise models.Survey.DoesNotExist()
        survey.set_caching(getattr(settings, 'POLLSTER_USE_CACHE', False))
        user_id = survey_user.user.id
        global_id = survey_user.global_id
        model = survey.as_model()
        r = model.objects.filter(user=user_id).filter(global_id = global_id).order_by('timestamp').reverse()[:1]
        if len(r) > 0:
            return r[0]
        return False



class SurveyContext(object):
    """
        Running context for a survey
        Hold all data about a survey's run.
        Instance of this class is transmitted to survey hook methods

    """

    def __init__(self, request, survey):
        self.request = request
        self.survey = survey
        self.survey_user = None
        self.form = None
        self.language = None
        self.last_data = None
        self.timestamp_last_fill = None
        self.template = 'pollster/survey_run.html'

    def set_last_data(self, last_data):
        if last_data is not None:
            # Prefill timestamp : template behaviour is to show the last time if this timestamp is defined
            # This value could be overriden by hooks to avoid this last time to be showed
            # That's why template does not use directly the value from the last data
            self.timestamp_last_fill = last_data.get('timestamp', None)
        self.last_data = last_data

    def get_template_data(self):
        """
         get the data ready to be transmitted to the survey template
        """
        # Check if url contains debug flag
        pollster_debug = self.request.GET.get('pollster_debug', False)

        return {
          "language": self.language,
          "locale_code": get_locale(self.language),
          "survey": self.survey,
          "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
          "last_participation_data_json": as_json(self.last_data),
          "form": self.form,
          "timestamp_last_fill": self.timestamp_last_fill,
          "pollster_debug": pollster_debug,
          "person": self.survey_user,
        }

class SurveyRunner(object):
    """
        Survey Runner Handler
    """
    def __init__(self):
        self.before_hooks = []
        self.before_save_hooks = []
        self.after_save_hooks = []
        self.before_render_hooks = []
        # Load hooks
        self.load_hooks()

    def load_hooks(self):
        workflows = get_workflows()
        for hook in workflows:
            if hasattr(hook, 'before_run'):
                self.before_hooks.append(hook.before_run)
            if hasattr(hook, 'before_save'):
                self.before_save_hooks.append(hook.before_save)
            if hasattr(hook, 'after_save'):
                self.after_save_hooks.append(hook.after_save)
            if hasattr(hook, 'before_render'):
                self.before_render_hooks.append(hook.before_render)

    def _log_hook(self, hook):
        cn = hook.__self__.__class__.__name__
        logger.debug(cn + ':'  + hook.__name__ )

    def run(self, request, survey_user, shortname):
        """
            Run the survey [shortname] for the [survey_user]
        """

        use_cache = getattr(settings, 'POLLSTER_USE_CACHE', False)
        survey = get_object_or_404(models.Survey, shortname=shortname, status='PUBLISHED')
        if use_cache:
            survey.set_caching(True)

        survey_context = SurveyContext(request, survey)

        language = get_language()

        survey_context.language = language

        # Get survey user
        user_id = request.user.id
        global_id = survey_user and survey_user.global_id

        survey_context.survey_user = survey_user

        # Run before hook
        for hook_method in self.before_hooks:
            if DEBUG:
                self._log_hook(hook_method)
            response = hook_method(survey_context)
            if response and isinstance(response, HttpResponse):
                return response

        # Prepare survey to be run
        translation = views.get_object_or_none(models.TranslationSurvey, survey=survey, language=language, status="PUBLISHED")
        if use_cache and translation is not None:
            translation.prefetch_tranlations()
        survey.set_translation_survey(translation)

        form = None

        # Now check if response has been submitted
        if request.method == 'POST':
            data = request.POST.copy()
            data['user'] = user_id
            data['global_id'] = global_id
            data['timestamp'] = datetime.datetime.now()
            form = survey.as_form()(data)
            survey_context.form = form
            if form.is_valid():

                # Run before_save hooks
                # before_save can modify stored data
                # Or run extra check before save the data
                for hook_method in self.before_save_hooks:
                    if DEBUG:
                        self._log_hook(hook_method)
                    response = hook_method(survey_context)
                    if response and isinstance(response, HttpResponse):
                        return response

                # Now save the data
                form.save()

                # Ask for hooks for a response
                next_url = reverse('group_management') # default is group management page
                for hook_method in self.after_save_hooks:
                    if DEBUG:
                        self._log_hook(hook_method)
                    response = hook_method(survey_context)
                    if DEBUG:
                        logger.debug(response)
                    if response and isinstance(response, HttpResponse):
                        return response
                    if response and isinstance(response, basestring):
                        next_url = response
                        break

                next_url = update_url_params(next_url, {"gid": global_id})
                return HttpResponseRedirect(next_url)
            else:
                survey.set_form(form)

        if DEBUG:
            logger.debug("Loading prefill data")
        survey_context.set_last_data(survey.get_prefill_data(user_id, global_id))

        for hook_method in self.before_render_hooks:
            if DEBUG:
                self._log_hook(hook_method)
            response = hook_method(survey_context)

        return render_to_response(survey_context.template, survey_context.get_template_data(), context_instance=RequestContext(request))