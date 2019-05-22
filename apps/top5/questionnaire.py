from django.template import Context, loader, Template

from .models import Service, PartTemplate, Ranking, Part

#def create_message(user, message, language, next = None, tracker = None):
#    if language:
#        activate(language)
#
#    t = Template(message.message)
#    c = {
#        'url': get_url(user, next),
#        'unsubscribe_url': get_login_url(user, reverse('apps.reminder.views.unsubscribe')),
#        'first_name': user.first_name,
#        'last_name': user.last_name,
#        'username': user.username,
#    }
#    c.update(site_context())
    # can be provided by site_context
#    c['site_logo'] = get_site_url() + c['site_logo']
#    c['site_url'] = get_site_url()
#    inner = t.render(Context(c))
#    template = 'reminder/message.html'

#    if message.html_template is not None and message.html_template != "":
#        template = message.html_template
#    t = loader.get_template(template)
#    c['inner'] = inner
#    c['MEDIA_URL'] = get_media_url()
#    c['message'] = message
#    c['tracking_url'] = get_tracking_url(tracker)
#    return inner, t.render(Context(c))

def create_service(service):
    service_dic = {}
    parts = Part.objects.filter(service = service)
    service_dic(zip(service, parts))
    return service_dic

def create_question(id_question, user):
    temp = ""
    template = loader.get_template('service.html')
    return temp
