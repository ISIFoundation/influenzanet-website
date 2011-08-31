import unittest
from datetime import datetime, timedelta, date

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

from mock import Mock, patch, patch_object

from .send import create_message
from .models import UserReminderInfo, ReminderSettings, NewsLetter, NewsLetterTemplate, get_upcoming_dates, get_prev_reminder_date, get_prev_reminder, get_reminders_for_users

class ReminderTestCase(unittest.TestCase):
    def setUp(self):
        ReminderSettings.objects.all().delete()
        NewsLetter.objects.all().delete()
        NewsLetterTemplate.objects.all().delete()

        self.old_languages = settings.LANGUAGES
        settings.LANGUAGES = (('en', 'English'), ('de', 'German'), ('fr', 'French'))

    def tearDown(self):
        settings.LANGUAGES = self.old_languages

    def test_get_upcoming_updates(self):
        def test(first_date, last_date, result):
            result = list(result) 
            self.assertEqual(first_date, result[0][0])
            self.assertEqual(last_date, result[-1][0])

        site = Site.objects.get()

        self.assertEquals([], list(get_upcoming_dates(datetime(2010, 10, 1, 15, 0, 0))))

        settings = ReminderSettings.objects.create(
            site=site,
            send_reminders=False,
            begin_date=datetime(2010, 9, 1, 14, 0, 0),
            interval=14,
        )

        self.assertEquals([], list(get_upcoming_dates(datetime(2010, 10, 1, 15, 0, 0))))

        settings.send_reminders = True
        settings.save()

        test(datetime(2010, 10, 13, 14, 0), datetime(2010, 12, 8, 14, 0), get_upcoming_dates(datetime(2010, 10, 1, 15, 0, 0)))
         
    def test_get_prev_reminder_date(self):
        site = Site.objects.get()

        self.assertEquals(None, get_prev_reminder_date(datetime(2010, 12, 12)))

        settings = ReminderSettings.objects.create(
            site=site,
            send_reminders=False,
            begin_date=datetime(2010, 9, 1, 14, 0, 0),
            interval=7,
        )

        self.assertEquals(None, get_prev_reminder_date(datetime(2010, 12, 12)))

        settings.send_reminders = True
        settings.save()

        self.assertEquals(None, get_prev_reminder_date(datetime(2010, 9, 1, 13, 0, 0)))
        self.assertEquals(datetime(2010, 9, 1, 14, 0, 0), get_prev_reminder_date(datetime(2010, 9, 1, 14, 0, 0)))
        self.assertEquals(datetime(2010, 9, 1, 14, 0, 0), get_prev_reminder_date(datetime(2010, 9, 8, 13, 0, 0)))
        self.assertEquals(datetime(2010, 9, 8, 14, 0, 0), get_prev_reminder_date(datetime(2010, 9, 8, 15, 0, 0)))

    def test_get_prev_reminder_with_newsletter(self):
        september_first = datetime(2010, 9, 1, 14, 0, 0)

        site = Site.objects.get()
        settings = ReminderSettings.objects.create(
            site=site,
            send_reminders=True,
            begin_date=september_first,
            interval=7,
        )

        newsletter = NewsLetter.objects.create(date=september_first, sender_email="test@example.org", sender_name="Test")
        newsletter.translate('en')
        newsletter.subject = "English subject"
        newsletter.message = "English message"
        newsletter.save()

        newsletter.translate('de')
        newsletter.subject = "German subject"
        newsletter.message = "German message"
        newsletter.save()

        result = get_prev_reminder(september_first)

        self.assertEqual("test@example.org", result['en'].sender_email)
        self.assertEqual("English subject", result['en'].subject)
        self.assertEqual("German subject", result['de'].subject)
        self.assertFalse('fr' in result)

    def test_get_prev_reminder_with_template(self):
        september_first = datetime(2010, 9, 1, 14, 0, 0)

        site = Site.objects.get()
        settings = ReminderSettings.objects.create(
            site=site,
            send_reminders=True,
            begin_date=september_first,
            interval=7,
        )

        template = NewsLetterTemplate.objects.create(is_default_reminder=True, sender_email="test@example.org", sender_name="Test")
        template.translate('en')
        template.subject = "English subject"
        template.message = "English message"
        template.save()

        template.translate('de')
        template.subject = "German subject"
        template.message = "German message"
        template.save()

        result = get_prev_reminder(september_first)

        self.assertEqual("test@example.org", result['en'].sender_email)
        self.assertEqual("English subject", result['en'].subject)
        self.assertEqual("German subject", result['de'].subject)
        self.assertFalse('fr' in result)

    def test_get_reminders_for_users(self):
        september_first = datetime(2010, 9, 1, 14, 0, 0)

        site = Site.objects.get()
        settings = ReminderSettings.objects.create(
            site=site,
            send_reminders=True,
            begin_date=september_first,
            interval=7,
        )

        newsletter = NewsLetter.objects.create(date=september_first, sender_email="test@example.org", sender_name="Test")
        newsletter.translate('en')
        newsletter.subject = "English subject"
        newsletter.save()

        newsletter.translate('de')
        newsletter.subject = "German subject"
        newsletter.save()

        for i, (language, active, last_reminder, expected) in enumerate([
            ('en', False, None, None),              # inactive: don't send
            (None, True, None, "English subject"),  # no language set: use default language
            ('en', True, None, "English subject"),  # english: use english
            ('de', True, None, "German subject"),   # german: use german
            ('fr', True, None, "English subject"),   # french not available: use default language
            ('en', True, september_first, None),    # already sent, don't send again
        ]):

            user = User.objects.create(username="user%s" % i)
            info = UserReminderInfo.objects.create(user=user, last_reminder=last_reminder, active=active, language=language)

            result = list(get_reminders_for_users(september_first, User.objects.filter(id=user.id)))
            if expected is None:
                self.assertEqual([], result)
            else:
                self.assertEqual(1, len(result))
                self.assertEqual(expected, result[0][1].subject, "%s, %s, %s, '%s' failed with actual: '%s'" %(language, active, last_reminder, expected, result[0][1].subject))

    def test_create_message(self):
        user = User.objects.create(username="user")

        text_base, html = create_message(user, 'this is text')
        self.assertTrue('this is text' in text_base)
        self.assertTrue('<body' in html)
        self.assertTrue('this is text' in html)
        self.assertFalse('<body' in text_base)
