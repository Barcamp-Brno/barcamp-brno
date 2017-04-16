import re

from jinja2 import evalcontextfilter, Markup
from barcamp import app
from utils import stage_is_active, stage_in_past, sponsors_data
from workshops import translate_status
from login_misc import check_auth, check_admin
import markdown


_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
_emoji_re = re.compile(r'[^\w .-<>/?!,()*]+', re.UNICODE)
_spaces = re.compile(r'\s+')


@app.template_filter()
def md(value):
    return Markup(markdown.markdown(value))

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace(u'\r\n', u'<br/>') for p in _paragraph_re.split(value))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.template_filter()
@evalcontextfilter
def no_emoji(eval_ctx, value):
    result = _emoji_re.sub('', value)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def extract_speakers(value):
    words = _spaces.sub(' ', _emoji_re.sub('', value)).split(' ')
    count = len(words)
    speakers = []

    if count <= 3:
        speakers.append(" ".join(words))
    else:
        speakers.append(" ".join(words[:2]))
        speakers.append(" ".join(words[2:]))
    return speakers

@app.context_processor
def speakers():
    return {'extract_speakers': extract_speakers}

@app.context_processor
def stage():
    return {'stage': stage_is_active}


@app.context_processor
def workshop_status():
    return {'status': translate_status}


@app.context_processor
def sponsors():
    return {
        'sponsors': {
            'main': [
            ],
            'regular': [
            ],
            'medial': [
            ],
        }
    }

@app.context_processor
def sponsors_d():
    return {
        'sponsors_data': sponsors_data,
    }


@app.context_processor
def after_stage():
    return {'after_stage': stage_in_past}


@app.context_processor
def going():
    return {'going': lambda user, year: user and 'going_%s' % year in user.keys() and user['going_%s' % year]}


@app.context_processor
def user():
    return {'user': check_auth()}

@app.context_processor
def admin():
    return {'admin': check_admin}