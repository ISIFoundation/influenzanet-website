# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Service(models.Model):
    name = models.CharField(max_length=60)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    selected = models.BooleanField(_("Is default selected"), help_text=_("If this option is checked this service will be in the pollster."))

    #rename : text_html
    text_html = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)

    class Meta:
        #Permet de definir le nom de la table
        db_table = 'Service'
        #ordering = ("-points",)
    def __unicode__(self):
        return self.name

# TODO : ameliorer le try
def get_service(service_id):
    try :
        service = Service.objects.get(id = service_id)
        if not service :
            print("No service found")
            return None
        print("Service(s) found")
        return service
    except Service.DoesNotExist:
        pass

class Ranking(models.Model):
    user = models.ForeignKey(User , null=True)
    service_id = models.ForeignKey(Service)
    creation_date = models.DateTimeField('creation date', blank=True, null=True)
    ranking_date = models.DateTimeField('ranking date', blank=True, null=True)
    modif_date = models.DateTimeField('modification date', blank=True, null=True)
    validation_date = models.DateTimeField('final validation date', blank=True, null=True)
    pertinency = models.IntegerField(default=0, blank=False, null=True)
    temporary_rank = models.IntegerField(default=0, blank=False, null=True)
    rank = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'RankingService'
        unique_together = ('user', 'service_id',)

class PartTemplate(models.Model):
    part_name = models.CharField(max_length=60)
    order = models.IntegerField(default=None, blank=True, null=True) #ChoiceField?
    title_style = models.CharField(max_length=60, blank=True, null=True)
    width = models.CharField(max_length=60, blank=True, null=True)

    def __unicode__(self):
        return self.part_name

    class Meta:
        db_table = 'PartTemplate'

def formating_part(part):
    #part.class_name
    start_div = ""
    end_div = ""
    if(part.special_style):
        special_style = "style="+str(part.special_style)
    else:
        special_style=""
    #tres mauvaise technique pour l'ajout d'un div plus grand. A ameliorer?
    if part.part_type.order == 4 :
        start_div = '<div class="effic_tolerance">'
    else :
        if part.part_type.order == 5 :
            end_div = '</div>'
    text = start_div+'<div class="'+ part.part_type.part_name +'" '+special_style+'>'+part.text+'</div>'+end_div
    return text


class Part(models.Model):
    title = models.CharField(max_length=60)
    service = models.ForeignKey(Service)
    part_type = models.ForeignKey(PartTemplate)
    text = models.TextField( blank=True, null=True)
    special_style = models.CharField( max_length=60 , blank=True, null=True)

    def __unicode__(self):
        return self.title