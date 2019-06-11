from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.conf import settings
from apps.partnersites.context_processors import site_context
import re
from django.template.base import TemplateDoesNotExist, Context
from django.core.mail.message import EmailMessage

def create_message_from_template(template_name, data, wrap_layout=True):
    """
        Create an email message from templates

        Expect 3 kind of files:
            [template_name]_subject.txt : subject template
            [template_name].txt : body text template
            [template_name].html: template contents for html version

        Parameters
        ----
        template_name: str
            template prefix (path and template name without extension)
        data: dict
            Data dictionnary used to bind values into template

        wrap_layout: bool
            If true use html base email layout and wrap contents with it

    """

    subject = render_to_string(template_name +'_subject.txt', dictionary=data)

    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    html_content = None
    text_content = None

    ctx = Context(data)

    try:
        template = get_template(template_name +'.html')
        html_content = template.render(ctx)
    except TemplateDoesNotExist:
        pass

    try:
        template = get_template(template_name +'.txt')
        text_content = template.render(ctx)
    except TemplateDoesNotExist:
        pass

    if html_content is None and text_content is None:
        raise Exception("At least one template type should be used")

    if text_content is None:
        text_content = html_content
        text_content = re.sub(r'< */p>','</p>\n\n', text_content)
        text_content = re.sub(r'< *br */? *>','<br>\n\n', text_content)
        text_content = strip_tags(text_content)
        text_content = re.sub(r'\n\n\n+','\n\n', text_content)

    if html_content is not None and wrap_layout:
            context = site_context(with_url=True)
            context['inner_contents'] = html_content
            context['email_subject'] = subject
            html_content = render_to_string("base/email_layout.html", context)

    return {
        'subject': unicode(subject),
        'html': html_content,
        'text': text_content,
    }

def create_email_message(subject, text=None, html=None):
    """
        Create message structure usable with send_message
    """
    if text is None and html is None:
        raise Exception("At least one html or text should be provided")

    return {
        'subject': subject,
        'html': html,
        'text': text,
    }


def send_message(email, message, use_prefix=True):
    """
    Send an email message

    Parameters
    ---------
        email: str
            email address to send to
        message: dict
            dict with subject, html, text keys. Can use create_email_message
    """

    headers = {
     'Sender': settings.EMAIL_DEFAULT_SENDER,
     'Return-Path': settings.EMAIL_DEFAULT_SENDER,
     'Reply-To': settings.EMAIL_CONTACT_TEAM,
     'From': settings.DEFAULT_FROM_EMAIL
    }

    if message['html']:
        msg = EmailMultiAlternatives(headers=headers)
        msg.attach_alternative(unicode(message['html']), "text/html")
    else:
        if not message['text']:
            raise Exception("Email message doesnt contains text content")
        msg = EmailMessage(headers=headers)

    subject = unicode(message['subject'])
    if use_prefix:
        subject = settings.EMAIL_SUBJECT_PREFIX + subject

    msg.subject = subject

    if isinstance(email, list):
        msg.to = email
    else:
        msg.to = [email]
    msg.body = unicode(message['text'])
    msg.send()
    return True

def send_team_message(message):
    if hasattr(settings, 'EMAIL_CONTACT_TEAM'):
        send_message(settings.EMAIL_CONTACT_TEAM, message)
