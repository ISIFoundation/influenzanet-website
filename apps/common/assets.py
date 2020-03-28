from webassets import Bundle, Environment
from webassets.filter import Filter, register_filter
from django.conf import settings
from django.template import Template, Context
import os

env = Environment(directory=settings.MEDIA_ROOT, url=settings.MEDIA_URL)
env.debug = settings.DEBUG

def optional_file(file):
    """
    Include a file if exists, nothing if not
    """
    path = settings.MEDIA_ROOT
    if not path.endswith('/'):
        path += '/'
    path +=  file
    if os.path.exists(path):
        if env.debug:
            print "including %s" % path
        return file
    if env.debug:
        print "skipping %s" % path

    return Bundle()

class TemplateFilter(Filter):
    name = 'from_template'
    
    def output(self, _in, out, **kwargs):
        template = Template(_in.read())
        ctx = Context()
        out.write(template.render(ctx))

    def input(self, _in, out, **kwargs):
        out.write(_in.read())

register_filter(TemplateFilter)

css_config = {
  'gn_color1': '#007AB8',  # Blue #007AB8
  'gn_color2': '#7AB800',  # Green #7AB800
  'color_button_tofill': '#FF8C00'
}

# Very simple
def apply_config(_in, out,  **kw):
    
    template = _in.read()
    for var in sorted(css_config, key=len, reverse=True):
        value = css_config[var]
        v = '$' + var
        template = template.replace(v, value)
    out.write(template)

###
# Common application Bundles
###

js_base = Bundle(
     Bundle('sw/js/config.js', filters=(apply_config, )),
     'pollster/jquery/js/jquery-1.5.2.min.js',
     'sw/js/jquery-1.7.2.min.js',
     'pollster/jquery/js/jquery.tools.min.js',
     'sw/js/ui.jquerytools.js',
     'sw/js/jquery.browser.mobile.js',
     Bundle('sw/js/thirdparties.js'), #, filters='yui_js'
     Bundle('sw/sw.js'), #, filters='yui_js'
     'sw/js/cconsent.js',
     'sw/js/cconsent.sw.js',
     output='assets/base.js'
  )

js_mailcheck = Bundle(
   'sw/js/mailcheck.min.js',
   optional_file('assets/domains.js'),
   output='assets/mailchecker.js'                   
) 
 
js_survey_intro = Bundle(
 'sw/js/intro.min.js',
 'sw/js/survey.intro.js',
 output='assets/survey.intro.js'                         
) 
 
css_base = Bundle(
     'sw/css/_normalize.css',
     'sw/css/_base.css',                         
     'sw/css/layout.css',
     'sw/css/contents.css',
     'sw/css/menu.css',
     'sw/css/influenzanet.css',
     'sw/css/cconsent.css',
     'sw/css/survey.css',
     'sw/css/journal.css',
     'sw/css/widgets.css',
     'sw/css/facebox.css',
     'sw/css/feedback.css',
     'sw/css/avatars.css',
     'sw/css/users.css',
     'sw/css/user-group.css',
     'sw/css/tooltip.css',
     'sw/css/messages.css',
     'sw/css/cohort.css',
     'sw/css/pregnant.css',
     'sw/css/introjs.min.css',
     output='assets/base.css',
     filters=(apply_config, 'cssrewrite','cssmin',)
)
