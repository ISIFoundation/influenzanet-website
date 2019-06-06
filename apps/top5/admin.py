from os.path import join

from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.sites.models import Site
from django.conf import settings

from .models import Service, PartTemplate, Ranking, Part
from .forms import ServiceForm, PartTemplateForm, PartForm

class PartAdmin(admin.ModelAdmin):
    form = PartForm
    list_display = ('title','service', 'part_type') #option has_special_style?
    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',
        )]

admin.site.register(Part, PartAdmin)
#class ServiceTemplateAdmin(admin.ModelAdmin):

class PartInline(admin.StackedInline):
    model = Part
    extra = 1 # should be 6 already?

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',
        )]

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceForm
    list_display = ('name','fullname')
    inlines = [PartInline]

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]
admin.site.register(Service, ServiceAdmin)


class PartTemplateAdmin(admin.ModelAdmin):
    form = PartTemplateForm
    list_display = ('part_name', 'order')
admin.site.register(PartTemplate, PartTemplateAdmin)


class RankingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,{'fields': ['user']}),
        ('Rank Services', {'fields': ['service_id','pertinency','temporary_rank','rank']}),
        ('Date information', {'fields': ['creation_date','service_selection_date','top5_selection_date','closing_tab_date','modif_date','validation_date']})
    ]
    list_display = ('user', 'service_id', 'rank', 'temporary_rank', 'pertinency','creation_date','service_selection_date','modif_date','closing_tab_date','top5_selection_date', 'validation_date')
    #list_filter = [ 'Service_id']
    search_fields = ['user','service_id']

admin.site.register(Ranking, RankingAdmin)


