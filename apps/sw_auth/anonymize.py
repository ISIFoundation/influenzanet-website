## Handle anonymization of account
from django.core.urlresolvers import reverse
from .models import AnonymizeLog, AnonymizeRequest
import datetime
from apps.common.mail import send_message, create_message_from_template
from apps.common.mail import create_email_message, send_team_message
from django.utils.translation import ugettext_lazy as _
from .utils import EMAIL_TEMPLATE_PATH

class Anonymizer:
    """
    This class handles the anonymization of inactive user
    Users are warned by an email after [login_delay] days without a login
    If the renew their connexion
    """
    def __init__(self):
        self.waiting_delay = 12
        self.login_delay = 30 * 18

    def log(self, user, event):
        """
        Log an event on the user account
        """
        l = AnonymizeLog()
        l.user = user
        l.event = event
        l.save()

    def send_anonymized(self, user_id, user_email):
        # Send an email to tell the user his account has been anonymized
        message = create_message_from_template(EMAIL_TEMPLATE_PATH + 'account_deactivated', {'id':user_id})
        send_message(user_email, message)

    def send_warning(self, user):
        expires = datetime.datetime.now() + datetime.timedelta(days=self.waiting_delay + 1)
        next = reverse('deactivate_planned')
        token = user.create_login_token(usage_left=1, expires=expires, next=next)

        data = {'login_delay': self.login_delay, 'waiting_delay': self.waiting_delay, 'login_token': token.get_url(), 'account_id': user.id }
        message = create_message_from_template(EMAIL_TEMPLATE_PATH + 'deactivate_warning', data)
        send_message(user.email, message)

    def send_request(self, user):
        data = { 'id': user.id}
        message = create_message_from_template(EMAIL_TEMPLATE_PATH + 'account_close', data)
        send_message(user.email, message)

    def anonymize(self, user):
        """
            Don anonymize the account
        """
        email = user.email
        user.anonymize()
        self.send_anonymized(user.id, email)
        self.log(user, AnonymizeLog.EVENT_ANONYMISED)

    def warn(self, user, delay=None):
        d = datetime.date.today()
        if delay is not None:
            t = datetime.timedelta(days=delay)
            d = d + t
        user.anonymize_warn = d
        user.save()
        self.log(user, AnonymizeLog.EVENT_WARNING)
        self.send_warning(user)

    def cancel(self, user):
        user.anonymize_warn = None
        user.save()
        self.log(user, AnonymizeLog.EVENT_CANCELLED)

    def request_close(self, user):
        ano, created = AnonymizeRequest.objects.get_or_create(user=user)
        if created:
            self.log(user, AnonymizeLog.EVENT_REQUEST)
            self.send_request(user)
            send_team_message(create_email_message(_(u'Account Closing request'), _(u'A account closing request has been provided for account number %d') % (user.id)))
        return (ano, created)

    def cancel_request(self, user):
        try:
            ano = AnonymizeRequest.objects.get(user=user)
            ano.delete()
            self.log(user, AnonymizeLog.EVENT_CANCELLED)
        except AnonymizeRequest.DoesNotExist:
            pass