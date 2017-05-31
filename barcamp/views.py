# coding: utf-8

from barcamp import app
from flask import render_template, abort, send_from_directory
from login_misc import check_auth, get_account
from talks import get_talks, get_talks_dict, get_talks_by_type
from workshops import get_workshops, get_workshops_dict
from utils import markdown_static_page, markdown_markup, stage_is_active
from entrant import get_count, get_entrants
from vote import get_user_votes
from program import times
from models.tiles import Tiles
from models.sponsors import Sponsors
import os

@app.route("/", redirect_to="/%s/index.html" % app.config['YEAR'])
@app.route("/%s/" % app.config['YEAR'], redirect_to="/%s/index.html" % app.config['YEAR'])
@app.route("/%s/index.html" % app.config['YEAR'])
def index():
    talks, extra_talks = get_talks()
    workshops = get_workshops()
    tiles = Tiles(app.redis, app.config['YEAR'])
    sponsors = Sponsors(app.redis, app.config['YEAR'])

    stage_template = "index.html"
    if stage_is_active(app.config['YEAR'], 'END'):
        stage_template = "end.html"

    if stage_is_active(app.config['YEAR'], 'PREVIEW'):
        stage_template = "preview.html"

    return render_template(
        stage_template,
        times=times,
        entrant_count=get_count(),
        entrants=get_entrants()[:50],
        novinky=markdown_markup('novinky'),
        talks=talks, extra_talks=extra_talks,
        talks_dict=get_talks_dict(),
        workshops=workshops,
        hi_tiles=filter(lambda x: x['score'] > 10, tiles.get_all()),
        low_tiles=filter(lambda x: x['score'] <= 10, tiles.get_all()),
        sponsors=sponsors.get_all_by_type(),
    )


@app.route('/%s/ucastnici.html' % app.config['YEAR'])
def entrants():
    return render_template(
        "entrants.html",
        entrant_count=get_count(),
        entrants=reversed(get_entrants())
    )


@app.route('/%s/partneri.html' % app.config['YEAR'])
def sponsors():
    sponsors = Sponsors(app.redis, app.config['YEAR'])

    return render_template(
        "partneri.html",
        sponsors=sponsors.get_all_by_type(),
        sponsors_other=markdown_markup('sponsors_other'),
    )

@app.route('/%s/catering.html' % app.config['YEAR'])
def catering():
    sponsors = Sponsors(app.redis, app.config['YEAR'])

    return render_template(
        "catering.html",
        informace=markdown_markup('catering'),
        sponsors=sponsors.get_all_by_type(),
    )

@app.route('/%s/doprovodny-program.html' % app.config['YEAR'])
def co_program():
    sponsors = Sponsors(app.redis, app.config['YEAR'])

    return render_template(
        "doprovodny-program.html", 
        sponsors=sponsors.get_all_by_type(min_weight=-100),
    )


@app.route('/%s/pracovni-nabidky.html' % app.config['YEAR'])
def job_wall():
    return render_template(
        "job-wall.html"
    )


@app.route('/%s/prednasky.html' % app.config['YEAR'])
@app.route('/%s/program.html' % app.config['YEAR'])
def talks_all():
    user = check_auth()
    user_hash = None

    if stage_is_active(app.config['YEAR'], 'PROGRAM'):
        talks = get_talks_dict()
    else:
        talks = get_talks_by_type()

    if user:
        user_hash = user['user_hash']

    return render_template(
        "talks.html",
        talks=talks,
        times=times,
        user_votes=get_user_votes(user_hash)
    )

@app.route('/%s/workshopy.html' % app.config['YEAR'])
def workshops_all():
    if stage_is_active(app.config['YEAR'], 'WORKSHOPS-PROGRAM'):
        workshops = get_workshops_dict()
    else:
        workshops = get_workshops()

    return render_template(
        "workshops.html",
        times=times,
        workshops=workshops,
    )

@app.route('/profil/<user_hash>/')
def profile(user_hash):
    data = get_account(user_hash)
    if not data:
        abort(404)

    return render_template(
        'profil.html',
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


def archive_proxy(year, path):
    year = str(year)
    # send_static_file will guess the correct MIME type
    return send_from_directory(
        os.path.abspath('archive'),
        os.path.join(year, path)
    )


for year in app.config['YEAR_ARCHIVE']:
    app.add_url_rule(
        '/%s/<path:path>' % year,
        defaults={'year': year},
        view_func=archive_proxy
    )

