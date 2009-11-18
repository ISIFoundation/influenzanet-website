# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from epiweb.apps.survey import utils
from epiweb.apps.survey import models
from epiweb.apps.survey import example
from epiweb.apps.survey import profile_data

from epidb_client import EpiDBClient

from django.conf import settings

survey_form_helper = None
profile_form_helper = None

@login_required
def thanks(request):
    return render_to_response('survey/thanks.html')

@login_required
def index(request):

    global survey_form_helper
    if survey_form_helper is None:
        survey = example.survey()
        survey_form_helper = utils.SurveyFormHelper(survey, request.user)

    if request.method == 'POST':
        form = survey_form_helper.create_form(request.POST)
        if form.is_valid():
            id = utils.send_survey_response(request.user, form._survey, form.cleaned_data)
            utils.save_survey_response(request.user, form._survey, id)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.thanks'))
    else:
        form = survey_form_helper.create_form()

    #js = utils.generate_js_helper(example.survey
    jsh = utils.JavascriptHelper(example.survey(), request.user)
    js = jsh.get_javascript()

    return render_to_response('survey/index.html', {
        'form': form,
        'js': js
    })

@login_required
def profile_index(request):
    global profile_form_helper
    if profile_form_helper is None:
        survey = profile_data.UserProfile()
        profile_form_helper = utils.SurveyFormHelper(survey, request.user)

    if request.method == 'POST':
        form = profile_form_helper.create_form(request.POST)
        if form.is_valid():
            utils.send_profile(request.user, form._survey, form.cleaned_data)
            utils.save_profile(request.user, form.cleaned_data)
            return HttpResponseRedirect(reverse('epiweb.apps.survey.views.profile_index'))
            
    else:
        form = profile_form_helper.create_form(utils.get_profile(request.user))

    jsh = utils.JavascriptHelper(profile_data.UserProfile(), request.user)
    js = jsh.get_javascript()

    return render_to_response('profile/index.html', {
        'form': form,
        'js': js
    })

