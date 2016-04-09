import re

from jinja2 import evalcontextfilter, Markup
from barcamp import app
from utils import stage_is_active, stage_in_past
from workshops import translate_status
from login_misc import check_auth

_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
   result = u'\n\n'.join(u'<p>%s</p>' % p.replace(u'\r\n', u'<br/>') for p in _paragraph_re.split(value))
   if eval_ctx.autoescape:
       result = Markup(result)
   return result


@app.context_processor
def stage():
    return {'stage': stage_is_active}


@app.context_processor
def workshop_status():
    return {'status': translate_status}


@app.context_processor
def after_stage():
    return {'after_stage': stage_in_past}


@app.context_processor
def going():
	return {'going': lambda user, year: user and 'going_%s' % year in user.keys() and user['going_%s' % year]}


@app.context_processor
def user():
    return {'user': check_auth()}