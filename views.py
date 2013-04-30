# coding: utf-8

from barcamp import app
from flask import render_template
from login_misc import check_auth
from talks import get_talks
from utils import menu, markdown_static_page, markdown_markup


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
