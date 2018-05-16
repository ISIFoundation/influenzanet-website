from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.conf import settings
from apps.partnersites.context_processors import site_context
import re
from django.template.base import TemplateDoesNotExist, Context

def create_message_from_template(template_name, data, wrap_layout=True):

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
