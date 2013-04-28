# coding: utf-8

from barcamp import app
from flask import render_template, Markup, abort
import markdown
from login_misc import check_auth
from talks import get_talks


@app.route("/")
def index():
    return render_template(
        "index.html",
        user=check_auth(),
        menu=menu(),
        sponsors_main=markdown_markup('sponsors_main'),
        talks=get_talks())


@app.route('/partneri/')
def sponsors():
    return render_template(
        "partneri.html",
        user=check_auth(),
        menu=menu(),
        sponsors_main=markdown_markup('sponsors_main'),
        sponsors=markdown_markup('sponsors'),
        sponsors_other=markdown_markup('sponsors_other'),
    )


@app.route("/page/")
def test():
    return render_template("page.html", user=check_auth(), menu=menu())


@app.route("/stranka/<page>/")
def static_page(page):
    return markdown_static_page(page)


def markdown_static_page(page):
    try:
        with open('data/brno2013/%s.md' % page) as f:
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
        with open('data/brno2013/%s.md' % filename) as f:
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
