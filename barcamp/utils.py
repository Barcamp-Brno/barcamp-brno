# coding: utf-8
from flask import render_template, Markup, abort
from flask import request
from login_misc import check_auth
import markdown
from barcamp import app
from datetime import datetime
from flask.ext.mail import Mail, Message
from copy import copy

from models.pages import Pages

def send_feedback_mail(subject, template, data, user, url):
    mail = Mail(app)
    body = read_file(template) or ""

    data = copy(data)
    data['ip'] = request.remote_addr
    data['user_agent'] = request.user_agent
    data['url'] = url
    data.update(user)
    body = body % data

    msg = Message(
        subject,
        recipients=["petr@joachim.cz"],
        sender=(user['name'], user['email'])
    )
    msg.body = body
    msg.html = markdown.markdown(body)
    mail.send(msg)


def markdown_static_page(uri):
    pages = Pages(app.redis, app.config['YEAR'])
    page = pages.get(uri)

    if not page:
        abort(404)

    return render_template(
        '_markdown.html',
        content=Markup(markdown.markdown(page['body'])),
        title=page['title'],
        user=check_auth())


def sponsors_data(sponsor, data):
    try:
        with open(
                'data/{year}/sponsors/{sponsor}/{data}.md'.format(** {
                    'year': app.config['YEAR'],
                    'sponsor': sponsor,
                    'data': data,
                })) as f:
            raw_data = f.read().decode('utf-8')
            content = Markup(markdown.markdown(raw_data))
    except:
        content = None

    if not content:
        content = Markup('')

    return content


def markdown_markup(filename):
    pages = Pages(app.redis, app.config['YEAR'])
    page = pages.get(filename)

    if page:
        content=Markup(markdown.markdown(page['body']))
    else:
        content=Markup('')

    return content

def stage_is_active(year, stage):
    if stage not in app.config['YEAR_SCHEDULE'][year]['STAGES']:
        return False

    schedule = app.config['YEAR_SCHEDULE'][year]['STAGES'][stage]
    day = datetime.now() if 'TEST_DATE' not in app.config else app.config['TEST_DATE']
    return schedule['from'] <= day and day <= schedule['to']

def stage_in_past(year, stage):
    if stage not in app.config['YEAR_SCHEDULE'][year]['STAGES']:
        return False

    schedule = app.config['YEAR_SCHEDULE'][year]['STAGES'][stage]
    day = datetime.now() if 'TEST_DATE' not in app.config else app.config['TEST_DATE']
    return day > schedule['to']

### MAIL ###
def send_mail(subject, to, message_file, url=""):
    mail = Mail(app)
    body = read_file(message_file) or ""
    body = body % {
        'url': url,
        'ip': request.remote_addr,
        'user_agent': request.user_agent,
        'mail': to,
    }

    msg = Message(
        subject,
        recipients=[to],
        sender=(u"Petr Joachim", "petr@joachim.cz")
    )
    msg.body = body
    msg.html = markdown.markdown(body)
    mail.send(msg)


def mail(subject, sender, recipient, file, data, sender_name=None):
    body = read_file(file) or ""

    body = body % data
    if sender_name:
        sender = (sender_name, sender)

    msg = Message(
        subject,
        sender=sender,
        recipients=[recipient]
    )

    msg.body = body
    msg.html = markdown.markdown(body)

    mail = Mail(app)
    return mail.send(msg)


def read_file(filename):
    return open(filename).read().decode('utf-8')