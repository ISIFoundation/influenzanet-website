import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings

from nani.models import TranslatableModel, TranslatedFields

from apps.survey.models import SurveyUser

# A short word on terminology:
# "Reminder" may refer to a NewsLetter object, or simply a placeholder
# that's based on the is_default_reminder NewsLetterTemplate

NO_INTERVAL = -1
WEEKLY_WITH_BATCHES = -2


class UserReminderInfo(models.Model):
    user = models.ForeignKey(User, unique=True)
    last_reminder = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField()
    language = models.CharField(max_length=5, blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    def get_language(self):
        if not self.language:
            return settings.LANGUAGE_CODE
        return self.language


class ReminderSettings(models.Model):
    site = models.OneToOneField(Site)
    send_reminders = models.BooleanField(_("Send reminders"), help_text=_("Check this box to send reminders"))
    interval = models.IntegerField(_("Interval"), choices=((7 ,_("Weekly")), (14,_("Bi-weekly")), (NO_INTERVAL, _("Don't send reminders at a fixed interval")), (WEEKLY_WITH_BATCHES, "Send exactly 7 days after the last action was taken.")), null=True, blank=True)
    begin_date = models.DateTimeField(_("Begin date"), help_text="Date & time of the first reminder and point of reference for subsequent reminders; (Time zone: %s)" % settings.TIME_ZONE, null=True, blank=True)
    batch_size = models.IntegerField("Batch size", null=True, blank=True, help_text="Batch size determines the max. sent emails per call to 'reminder_send'; choose in coordinance with you r crontab interval and total users; Leave empty to not have any maximum")
    currently_sending = models.BooleanField("Currently sending", help_text="This indicates if the reminders are being sent right now. Don't tick this box unless you absolutely know what you're doing", default=False)
    last_process_started_date = models.DateTimeField("Last process started at", help_text="This indicates if the reminders are being sent right now. Don't change this value unless you absolutely know what you're doing")

    send_resubscribe_email = models.BooleanField(default=False, help_text=u"An email will be sent when the user unsubscribes with information on how to resubscribe.")
    resubscribe_email_subject = models.CharField(blank=True, max_length=255)
    resubscribe_email_message = models.TextField(blank=True, help_text=u"The strings {{ resubscribe_url }} and {{ url }} may be used as variables.")

    def __unicode__(self):
        return _(u"Reminder settings")

    def get_interval(self):
        if self.interval == WEEKLY_WITH_BATCHES:
            return 7
        return self.interval

class NewsLetterTemplate(TranslatableModel):
    is_default_reminder = models.BooleanField(_("Is default reminder"), help_text=_("If this option is checked this template is the standard template for reminder emails."))
    is_default_newsitem = models.BooleanField(_("Is default newsitem"), help_text=_("If this option is checked this template is the standard template for new news items."))
    sender_email = models.EmailField(_("Sender email"), help_text="Only use email addresses for your main domain to ensure deliverability")
    sender_name = models.CharField(_("Sender name"), max_length=255)

    translations = TranslatedFields(
        subject = models.CharField(max_length=255),
        message = models.TextField(help_text="The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url."),
    )

    def __unicode__(self):
        return self.subject

class NewsLetter(TranslatableModel):
    date = models.DateTimeField(_("Date"), unique=True, choices=[])

    sender_email = models.EmailField(_("Sender email"), help_text="Only use email addresses for your main domain to ensure deliverability")
    sender_name = models.CharField(_("Sender name"), max_length=255)

    published = models.BooleanField("Is published", help_text="Uncheck this box to postpone sending of this newsletter until the box is checked.", default=True)

    userlist = models.CharField(_("Table or view name used to get the user list"), max_length=255, blank=True, null=True)

    next = models.CharField(_("Next page to follow"), max_length=255, blank=True, null=True)

    html_template = models.CharField(_("Email template"), max_length=255, blank=True, null=True)

    translations = TranslatedFields(
        subject = models.CharField(max_length=255),
        message = models.TextField(help_text="The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url."),
    )

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ("-date",)

class NewsletterTracking(models.Model):
    user = models.ForeignKey(User)
    newsletter = models.ForeignKey(NewsLetter)
    date_sent = models.DateTimeField(null=True, blank=True)
    tracking = models.IntegerField(default=0)
    first_view = models.DateTimeField(null=True, blank=True)


class MockNewsLetter(object):
    def __init__(self):
        self.date = self.sender_email= self.sender_name = self.subject = self.message = self.next = None

class ReminderError(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    message = models.CharField(max_length=255)
    traceback = models.TextField()

    def __unicode__(self):
        return self.message

    class Meta:
        ordering = ("-timestamp",)

    def email(self):
        return self.user.email

def get_settings():
    if ReminderSettings.objects.count() == 0:
        return None
    return ReminderSettings.objects.all()[0]

def get_upcoming_dates(now):
    settings = get_settings()
    if not settings or not settings.send_reminders or not settings.begin_date:
        raise StopIteration()

    if settings.get_interval() < 0:
        yield now, "Current newsletter"
        raise StopIteration()

    to_yield = 7
    current = settings.begin_date

    while to_yield > 0:
        if current >= now - datetime.timedelta(2 * settings.get_interval()):
            diff = current - now
            days = abs(diff.days) % 7
            weeks = abs(diff.days) / 7
            if diff.days > 0:
                if weeks == 0:
                    yield current, _("%(current)s (in %(days)s days)") % locals()
                else:
                    yield current, _("%(current)s (in %(weeks)s weeks)") % locals()
            else:
                if weeks == 0:
                    yield current, _("%(current)s (%(days)s days ago)") % locals()
                else:
                    yield current, _("%(current)s (%(weeks)s weeks ago)") % locals()
            to_yield -= 1
        current += datetime.timedelta(settings.get_interval())

def get_default_for_reminder(language):
    if NewsLetterTemplate.objects.language(language).filter(is_default_reminder=True).count() == 0:
        return None
    return NewsLetterTemplate.objects.language(language).filter(is_default_reminder=True)[0]

def get_default_for_newsitem(language):
    if NewsLetterTemplate.objects.language(language).filter(is_default_newsitem=True).count() == 0:
        return None
    return NewsLetterTemplate.objects.language(language).filter(is_default_newsitem=True)[0]

def get_prev_reminder_date(now, published=True):
    """Returns the date of the previous reminder or None if there's no
    such date"""

    settings = get_settings()

    if not settings or not settings.send_reminders or not settings.begin_date or now < settings.begin_date:
        return None

    if settings.interval == NO_INTERVAL:
        qs = NewsLetter.objects.filter(date__lte=now).exclude(date__gt=now).order_by("-date")
        if published:
            qs = qs.filter(published=published)
        qs = list(qs)
        if len(qs) == 0:
            return None
        return qs[0].date

    current = settings.begin_date
    prev = settings.begin_date

    while True:
        if current >= now:
            return prev
        prev = current
        current += datetime.timedelta(settings.get_interval())

def get_prev_reminder(now, published=True):
    """Returns the reminder (newsletter/tempate) to send at a given moment
    as a dict with languages as keys, or None if there is no such reminder"""
    def p(qs):
        if published:
            return qs.filter(published=published)
        return qs

    prev_date = get_prev_reminder_date(now, published)
    if prev_date is None:
        return None

    if p(NewsLetter.objects.filter(date=prev_date)).count():
        result = {}
        for language, name in settings.LANGUAGES:
            if p(NewsLetter.objects.language(language).filter(date=prev_date)):
                result[language] = p(NewsLetter.objects.language(language)).get(date=prev_date)
        return result

    result = {}
    for language, name in settings.LANGUAGES:
        template = get_default_for_reminder(language)
        if template is None:
            continue

        newsletter = MockNewsLetter()
        newsletter.date = prev_date
        newsletter.sender_email = template.sender_email
        newsletter.sender_name = template.sender_name
        newsletter.subject = template.subject
        newsletter.message = template.message
        result[language] = newsletter

    return result

def get_reminders_for_users(now, users):
    reminder_dict = get_prev_reminder(now)
    if not reminder_dict:
        raise StopIteration()

    batch_size = get_settings().batch_size if get_settings() else None

    yielded = 0
    for user in users:
        if batch_size and yielded >= batch_size:
            raise StopIteration

        info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True, 'last_reminder': user.date_joined})

        if not info.active:
            continue

        language = info.get_language()
        if not language in reminder_dict:
            language = settings.LANGUAGE_CODE

        reminder = reminder_dict[language]

        if info.last_reminder is None:
            yield user, reminder, language
            yielded += 1
            continue

        if get_settings() and get_settings().interval == WEEKLY_WITH_BATCHES:
            survey_users = SurveyUser.objects.filter(user=user, deleted=False)
            if not survey_users.count():
                survey_user = SurveyUser.objects.create_survey_user(user=user)
                survey_users = SurveyUser.objects.filter(user=user, deleted=False)

            last_action_date = max(su.get_last_weekly_survey_date() for su in survey_users)
            if info.last_reminder and info.last_reminder > last_action_date:
                last_action_date = info.last_reminder

            last_action = (now - last_action_date).days
            last_action_long_ago_enough = last_action >= 7

            if not last_action_long_ago_enough:
                continue

            if last_action > 30: # assumed to be: at start of season, since no reminder were sent for a month
                if not last_action % 7 == 0:
                    continue # start up respecting a full-week difference with the last action (or reminder)
                    # this way the same partioning as used in the last season is maintained

        if info.last_reminder < reminder.date:
            yield user, reminder, language
            yielded += 1


