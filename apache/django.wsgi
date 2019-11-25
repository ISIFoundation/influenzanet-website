import os
import sys

apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
workspace=project
sys.path.append(workspace) 

sys.path.append(workspace+'/lib/python2.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#print >> sys.stderr, sys.path 

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
