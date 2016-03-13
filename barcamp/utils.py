# coding: utf-8
from flask import render_template, Markup, abort
from login_misc import check_auth
import markdown
from barcamp import app
from datetime import datetime

def markdown_static_page(page):
    try:
        with open('data/%s/%s.md' % (app.config['YEAR'], page)) as f:
            raw_data = f.read().decode('utf-8')
            content = Markup(markdown.markdown(raw_data))
    except:
        content = None
        if app.debug:
            raise

    if content is None:
        abort(404)

    return render_template(
        '_markdown.html',
        content=content,
        user=check_auth())


def markdown_markup(filename):
    try:
        with open('data/%s/%s.md' % (app.config['YEAR'], filename)) as f:
            raw_data = f.read().decode('utf-8')
            md_data = markdown.markdown(raw_data)
            md_data = md_data\
                .replace('<p>', '')\
                .replace('</p>', '')
            content = Markup(md_data)
    except:
        content = None

    if not content:
        content = Markup('')

    return content

def stage_is_active(year, stage):
    if stage not in app.config['YEAR_SCHEDULE'][year]['STAGES'].keys():
        return False

    schedule = app.config['YEAR_SCHEDULE'][year]['STAGES'][stage]
    day = datetime.now() if 'TEST_DATE' not in app.config else app.config['TEST_DATE']
    return schedule['from'] <= day and day <= schedule['to']

def stage_in_past(year, stage):
    if stage not in app.config['YEAR_SCHEDULE'][year]['STAGES'].keys():
        return False

    schedule = app.config['YEAR_SCHEDULE'][year]['STAGES'][stage]
    day = datetime.now() if 'TEST_DATE' not in app.config else app.config['TEST_DATE']
    return day > schedule['to']
