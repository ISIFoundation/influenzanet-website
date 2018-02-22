from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import re

def create_message_from_template(template, data, text_template=False, html_template=True):
    subject = render_to_string(template +'_subject.txt', dictionary=data)

    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    html_content = None
    text_content = None

    if not (html_template or text_template):
        raise Exception("At least one template type should be used")

    if html_template:
        html_content = render_to_string(template +'.html', dictionary=data)
        if not text_template:
            text_content = strip_tags(html_content)
            text_content = re.sub(r'\n\n\n+','\n\n', text_content)
    if text_template:
        text_content = render_to_string(template +'.txt', dictionary=data)

    return {
        'subject': subject,
        'html': html_content,
        'text': text_content,
    }

def create_email_message(subject, text=None, html=None):
    if text is None and html is None:
        raise Exception("At least one html or text should be provided")
    return {
        'subject': subject,
        'html': html,
        'text': text,
    }


def send_message(email, message):
    if message['html']:
        msg = EmailMultiAlternatives()
        msg.subject = message['subject']
        msg.body = message['text']
        msg.to = [email]
        msg.attach_alternative(message['html'], "text/html")
        msg.send()
    else:
        if not message['text']:
            raise Exception("No text content")
        send_mail(message['subject'], message['text'], None, [email])
    return True

def send_team_message(message):
    if hasattr(settings, 'EMAIL_CONTACT_TEAM'):
        send_message(settings.EMAIL_CONTACT_TEAM, message)
