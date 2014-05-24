# coding: utf-8

from barcamp import app
from flask import render_template, abort
from login_misc import check_auth, get_account
from talks import get_talks, get_talks_dict
from utils import menu, markdown_static_page, markdown_markup
from entrant import get_count, get_entrants
from vote import get_user_votes
from program import times
import os

@app.route("/", redirect_to="/%s/index.html" % app.config['YEAR'])
@app.route("/%s/" % app.config['YEAR'], redirect_to="/%s/index.html" % app.config['YEAR'])
@app.route("/%s/index.html" % app.config['YEAR'])
def index():
    user = check_auth()
    user_hash = None
    if "PROGRAM_READY" in app.config['STAGES']:
        talks = get_talks_dict()
        extra_talks = []
    else:
        talks, extra_talks = get_talks()

    if user:
        user_hash = user['user_hash']
    return render_template(
        "index.html",
        user=user,
        menu=menu(),
        times=times,
        entrant_count=get_count(),
        entrants=get_entrants()[:50],
        user_votes=get_user_votes(user_hash),
        novinky=markdown_markup('novinky'),
        sponsors_main=markdown_markup('sponsors_main'),
        sponsors=markdown_markup('sponsors'),
        talks=talks, extra_talks=extra_talks,
        talks_dict=get_talks_dict())


@app.route('/%s/ucastnici.html' % app.config['YEAR'])
def entrants():
    return render_template(
        "entrants.html",
        user=check_auth(),
        menu=menu(),
        entrant_count=get_count(),
        entrants=reversed(get_entrants())
    )


@app.route('/%s/partneri.html' % app.config['YEAR'])
def sponsors():
    return render_template(
        "partneri.html",
        user=check_auth(),
        menu=menu(),
        sponsors_main=markdown_markup('sponsors_main'),
        sponsors=markdown_markup('sponsors'),
        sponsors_other=markdown_markup('sponsors_other'),
    )

@app.route('/profil/<user_hash>/')
def profile(user_hash):
    data = get_account(user_hash)
    if not data:
        abort(404)

    return render_template(
        'profil.html',
        user=check_auth(),
        menu=menu(),
        profile=data
    )

def stranky():
    files = []
    for _, _, keys in os.walk('data/%s' % app.config['YEAR']):
        files += keys;

    return [{"page": key.replace(".md", "")} for key in files]

@app.route("/%s/stranka/<page>.html" % app.config['YEAR'], generator=stranky)
def static_page(page):
    return markdown_static_page(page)

@app.route('/2013/<path:path>')
def archive_proxy(path):
    # send_static_file will guess the correct MIME type
    print os.path.join('./archive/2013/', path)
    return app.send_static_file(os.path.join('./archive/2013/', path))
