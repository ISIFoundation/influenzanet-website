from webassets import Bundle
from apps.common.assets import apply_config

js_raphael = Bundle(
    "sw/js/raphael/raphael-min.js",
    "sw/js/raphael/g.raphael-min.js",
    "sw/js/raphael/g.bar-min.js",
    output='assets/raphael.js'
)

css_dashboard = Bundle(
    "sw/css/dashboard.css",
    output='assets/dashboard.css',
    filters=(apply_config, 'cssrewrite', 'cssmin',)
)