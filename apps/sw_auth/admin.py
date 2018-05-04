from django.contrib.admin import ModelAdmin
from django.contrib.admin import site
from .models import EpiworkUser, AnonymizeRequest

class EpiworkUserAdmin(ModelAdmin):
    list_display = ['login','email','is_active']
    exclude = ('user','password',)
    search_fields = ['user','email']

class AnonymizeRequestAdmin(ModelAdmin):
    list_display = ['user','date']
    search_fields = ['user','email']

site.register(EpiworkUser, EpiworkUserAdmin)

site.register(AnonymizeRequest, AnonymizeRequestAdmin)