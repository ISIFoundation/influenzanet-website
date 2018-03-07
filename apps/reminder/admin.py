from os.path import join

from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.sites.models import Site
from django.conf import settings

from nani.admin import TranslatableAdmin

from .models import UserReminderInfo, ReminderSettings, NewsLetterTemplate, NewsLetter, ReminderError, NewsletterTracking
from .forms import ReminderSettingsForm, NewsLetterTemplateForm, NewsLetterForm

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = 'Make selected reminders active'

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = 'Make selected reminders inactive'

class UserReminderInfoAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'active', 'last_reminder',)
    ordering = ('user__username',)
    actions = (make_active, make_inactive,)
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('user__username',)

    def get_actions(self, request):
        actions = super(UserReminderInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(UserReminderInfo, UserReminderInfoAdmin)

class UserReminderInfoInline(admin.StackedInline):
    model = UserReminderInfo

current_user_admin = type(admin.site._registry[User])
class InfoUserAdmin(current_user_admin):
    inlines = current_user_admin.inlines + [UserReminderInfoInline]

admin.site.unregister(User)
admin.site.register(User, InfoUserAdmin)

class SiteSettingsInline(admin.StackedInline):
    model = ReminderSettings
    form = ReminderSettingsForm

current_site_admin = type(admin.site._registry[Site])
class ReminderSiteAdmin(current_site_admin):
    inlines = current_site_admin.inlines + [SiteSettingsInline]

admin.site.unregister(Site)
admin.site.register(Site, ReminderSiteAdmin)

class NewsLetterTemplateAdmin(TranslatableAdmin):
    form = NewsLetterTemplateForm

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.register(NewsLetterTemplate, NewsLetterTemplateAdmin)

class NewsLetterAdmin(TranslatableAdmin):
    form = NewsLetterForm
    list_display = ("__unicode__", "date", "published", "userlist", "next", "html_template")

    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'js/lib/jquery.js',
            'js/lib/jquery.query.js',

        )]

admin.site.register(NewsLetter, NewsLetterAdmin)

class ReminderErrorAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "message", "user", "email")
    search_fields = ('user__username', 'user__email',)

admin.site.register(ReminderError, ReminderErrorAdmin)

class NewsletterTrackingAdmin(admin.ModelAdmin):
    list_display = ("id","user", "newsletter","date_sent", "tracking", "first_view")

admin.site.register(NewsletterTracking, NewsletterTrackingAdmin)

admin.site.register(ReminderSettings)
