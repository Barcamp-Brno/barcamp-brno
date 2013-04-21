import re

from jinja2 import evalcontextfilter, Markup, escape
from barcamp import app

_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
   result = u'\n\n'.join(u'<p>%s</p>' % p.replace(u'\r\n', u'<br/>') for p in _paragraph_re.split(value))
   if eval_ctx.autoescape:
       result = Markup(result)
   return result