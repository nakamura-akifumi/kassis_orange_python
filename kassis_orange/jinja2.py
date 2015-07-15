from jinja2 import Environment
from datetime import datetime
from app_search.helpers.jinja2_custom_filters import datetimeformat
from app_search.helpers.jinja2_custom_filters import checked

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'imananji': datetime.now,
    })
    env.filters['datetimeformat'] = datetimeformat
    env.filters['checked'] = checked
    return env
