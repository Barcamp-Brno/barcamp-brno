# coding: utf-8

from barcamp import app
from flask import render_template, Markup
import markdown
from login import check_auth


@app.route("/")
def index():
    return render_template("index.html", user=check_auth())


@app.route("/page/")
def test():
    return render_template("page.html", user=check_auth())


@app.route("/kontakty/")
def markdown_page():
    with open('data/brno2013/kontakty.md') as f:
        raw_data = f.read().decode('utf-8')
        content = Markup(markdown.markdown(raw_data))
    return render_template(
        '_markdown.html',
        content=content or "omg",
        user=check_auth())
