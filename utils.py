# coding: utf-8
from flask import render_template, Markup, abort
from login_misc import check_auth
import markdown
from barcamp import app


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
        menu=menu(),
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


def menu():
    return markdown_markup('menu')
