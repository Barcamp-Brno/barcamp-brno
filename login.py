# coding: utf-8

from flask import render_template
from barcamp import app


@app.route("/login/")
def login():
    return render_template("login.html")


@app.route("/login/twitter/")
@app.route("/login/facebook/")
@app.route("/login/zapomenute-heslo/")
@app.route("/login/old-school/", methods=["POST"])
@app.route("/login/registrace/")
@app.route("/logout/")
@app.route("/nastaveni-profilu/")
def todo():
    return "Tohle se pripravuje"
