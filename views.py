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
        talks=get_talks())


@app.route("/page/")
def test():
    return render_template("page.html", user=check_auth())


@app.route("/kontakty/")
def markdown_page():
    return markdown_static_page('kontakty')


@app.route("/stranka/<page>/")
def static_page(page):
    return markdown_static_page(page)


def markdown_static_page(page):
    try:
        with open('data/brno2013/%s.md' % page) as f:
            raw_data = f.read().decode('utf-8')
            content = Markup(markdown.markdown(raw_data))
    except:
        raise

    if not content:
        abort(404)

    return render_template(
        '_markdown.html',
        content=content,
        user=check_auth())
