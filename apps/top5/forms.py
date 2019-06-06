from datetime import datetime

from django import forms

from cms.plugins.text.widgets.wymeditor_widget import WYMEditor

from .models import Ranking, Service, PartTemplate, Part

from nani.forms import ModelForm

class ServiceForm(ModelForm):
    text_html = forms.CharField(widget=WYMEditor(), required=False)

    class Meta:
        model = Service
        fields = ['name','fullname', 'text_html']

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

class PartForm(ModelForm):
    text = forms.CharField(widget=WYMEditor())

    class Meta:
        model = Part
        fields = ['title', 'service','part_type', 'text','special_style' ]

    def __init__(self, *args, **kwargs):
        super(PartForm, self).__init__(*args, **kwargs)


class PartTemplateForm(ModelForm):

    class Meta:
        model = PartTemplate
        fields = ['part_name', 'order']

