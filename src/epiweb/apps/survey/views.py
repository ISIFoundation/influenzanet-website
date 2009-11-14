# -*- coding: utf-8 -*-

from django import forms
from django.template import Context, loader
from django.http import HttpResponse

from epiweb.apps.survey import utils
from epiweb.apps.survey.data import example

def index(request):

    if request.method == 'POST':
        form = utils.generate_form(example.data.sections[0], request.POST)
    else:
        form = utils.generate_form(example.data.sections[0])

    js = utils.generate_js_helper(example.data.sections[0])

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form,
        'js': js
    })
    return HttpResponse(t.render(c))

def survey(request, survey_id, page=None):
    html = "survey_id=%s, page=%s" % (survey_id, page)
    return HttpResponse(html)

