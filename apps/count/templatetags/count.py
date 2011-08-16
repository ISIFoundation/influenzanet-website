from __future__ import absolute_import

import urllib

from django.template import Library, Node
from django.contrib.sites.models import Site
from django.core.cache import cache 

register = Library()

FAKED = {
    'nl': '17952',
    'be': '4717',
    'de': '0',
    'at': '0',
    'se': '0',
    'uk': '703',
}

SOURCES = {
    'nl': 'http://www.grotegriepmeting.nl/count/counter/',
    'be': 'http://www.grotegriepmeting.be/count/counter/',
    'de': 'http://www.aktivgegengrippe.de/count/counter/',
    'at': 'http://www.aktivgegengrippe.at/count/counter/',
    'se': 'http://www.influensakoll.se/count/counter/',
    'uk': 'http://www.flusurvey.org.uk/count/counter/',
    'it': 'http://www.influweb.it/count/counter/',
    'pt': 'http://www.gripenet.pt/cgear/pt.php',
}

def do_member_count(parser, token):
    contents = token.split_contents()
    assert len(contents) == 2, "%r tag requires a single argument" % contents[0]
    country = contents[1]
    assert country[0] in ['"', "'"], "argument must be a string"
    country = country[1:-1]
    return MemberCountNode(country)

class MemberCountNode(Node):
    def __init__(self, country):
        self.country = country 

    @classmethod
    def get(cls, country):
        key = "count-counter-%s" % country
        if cache.get(key):
            return cache.get(key)

        if country in FAKED:
            return FAKED[country]

        try:
            result = urllib.urlopen(SOURCES[country]).read()
        except:
            result = '0'
        cache.set(key, result, timeout=60 * 30) # timeout 30 minutes

        try:
            int(result)
        except ValueError:
            return '0'

        return result 

    def render(self, context):
        if self.country == 'total':
            return "%s" % sum([int(self.get(country)) for country in SOURCES.keys()])

        return self.get(self.country)

register.tag('member_count', do_member_count)

