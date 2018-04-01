# coding: utf-8
from collections import defaultdict
from hashlib import md5

from flask_wtf import Form
from flask import render_template, request, json, flash, redirect
from flask import url_for, abort
from wtforms import TextField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, URL, Optional

from barcamp import app
from login_misc import check_auth, auth_required, get_account
from entrant import user_user_go
from utils import markdown_markup, send_feedback_mail
from vote import get_user_votes


KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
    'account': 'account_%s',
}

CATEGORIES = [
    ('business', u'Byznys'),
    ('design', u'Design'),
    ('inovations', u'Inovace'),
    ('marketing', u'Marketing'),
    ('inspirational', u'Osobní rozvoj'),
    ('development', u'Vývoj'),
]

def prednasky():
    return [{"talk_hash": key} for key in app.redis.zrange(KEYS['talks'], 0, -1)]

@app.route('/%s/prednaska/<talk_hash>.html' % app.config['YEAR'], generator=prednasky)
def talk_detail(talk_hash):
    talk = get_talk(talk_hash)
    if not talk:
        abort(404)

    author = get_account(talk['user'])

    user = check_auth()
    user_hash = None

    if user:
        user_hash = user['user_hash']

    return render_template(
        'talk_detail.html',
        talk=talk,
        user_votes=get_user_votes(user_hash),
        author=author
    )


@app.route('/prednaska/odstranit/<talk_hash>/')
@auth_required
def talk_delete(talk_hash):
    talk_data = get_talk(talk_hash)
    user_data = check_auth()

    if user_data['user_hash'] != talk_data['user']:
        abort(403)  # uzivatel nema pravo

    app.redis.delete(KEYS['talk'] % talk_hash)
    app.redis.zrem(KEYS['talks'], talk_hash)
    flash(u'Přednáška byla smazána', 'success')
    return redirect(url_for('index'))


@app.route(
    "/prednaska/pridat/",
    methods=['GET', 'POST'],
    defaults={'talk_hash': None})
@app.route("/prednaska/editace/<talk_hash>/", methods=['GET', 'POST'])
@auth_required
def talk_edit(talk_hash=None):
    talk_data = {}
    user_data = check_auth()
    if talk_hash:
        talk_data = get_talk(talk_hash)

        if user_data['user_hash'] != talk_data['user']:
            abort(403)  # uzivatel tohle nemuze editovat

    if request.method == "POST":
        form = TalkForm(request.form)
        if form.validate():
            old_hash = talk_hash
            talk_hash = create_or_update_talk(form.data, talk_hash)
            user_user_go(user_data)
            flash(u'Přednáška byla uložena', 'success')
            if talk_hash != old_hash:
                return redirect(url_for('talk_edit', talk_hash=talk_hash))
    else:
        form = TalkForm(**talk_data)
    return render_template(
        'talk_form.html',
        informace=markdown_markup('pro-prednasejici'),
        form=form,
        talk=talk_data
    )


def create_or_update_talk(data, talk_hash=None):
    user_data = check_auth()
    if talk_hash is None:
        talk_hash = get_talk_hash(data)
        data['talk_hash'] = talk_hash
        # send talk mail
        send_feedback_mail(
            u"Nová přednáška: %s" % data['title'],
            "data/new-talk.md",
            data,
            user_data,
            url_for('talk_detail', talk_hash=talk_hash, _external=True)
        )

    data.update({
        'user': user_data['user_hash'],
        'talk_hash': talk_hash,
    })

    app.redis.set(KEYS['talk'] % talk_hash, json.dumps(data))
    # zalozime hlasovani - bezpecne pres zincrby (namisto zadd s if podminkou)
    app.redis.zincrby(KEYS['talks'], talk_hash, 0)
    return talk_hash


def get_talk_hash(data, depth=5):
    "Non-colide talk hash algoritm ;)"
    talk_hash = md5("%s|%s" % (json.dumps(data), depth)).hexdigest()[:8]
    if not app.redis.setnx(KEYS['talk'] % talk_hash, 'false'):
        return get_talk_hash(data, depth - 1)

    return talk_hash


def get_talk(talk_hash):
    talk = json.loads(app.redis.get(KEYS['talk'] % talk_hash) or 'false')
    if not talk: 
        return False

    score = int(app.redis.zscore(KEYS['talks'], talk_hash))
    talk['score'] = score
    return talk


def get_talks(user_hash=None):
    talks = _get_talks()

    extra_talk_hashes = app.redis.smembers(KEYS['extra'])
    extra_talks = []
    ordinary_talks = []

    for talk in talks:
        if talk['talk_hash'] in extra_talk_hashes:
            extra_talks.append(talk)
        else:
            ordinary_talks.append(talk)

    return ordinary_talks, extra_talks

def get_talks_by_type():
    talks = _get_talks()

    talk_dict = defaultdict(list)
    for talk in talks:
        talk_dict[talk['category']].append(talk)

    import pprint
    pprint.pprint(talk_dict)
    return talk_dict


def get_talks_dict():
    talks = _get_talks()
    return dict([(talk['talk_hash'], talk) for talk in talks])


def _get_talks():
    talk_tuples = app.redis.zrevrange(KEYS['talks'], 0, -1, withscores=True)
    talk_hashes = [talk_tuple[0] for talk_tuple in talk_tuples]
    talk_scores = dict(talk_tuples)

    if not talk_hashes:
        return []

    talks = filter(
        lambda x: bool(x),
        map(
            lambda talk: json.loads(talk or 'false'),
            app.redis.mget(map(lambda key: KEYS['talk'] % key, talk_hashes))
        )
    )
    try:
        talks.remove(False)
        talks.remove(False)
        talks.remove(False)
        talks.remove(False)
        talks.remove(False)
    except:
        pass

    map(
        lambda talk: talk.update(
            {'score': int(talk_scores.get(talk['talk_hash']) or 0)}),
        talks
    )

    user_hashes = [talk['user'] for talk in talks]
    users_tuple = map(
        lambda user: json.loads(user or 'false'),
        app.redis.mget(map(lambda key: KEYS['account'] % key, user_hashes))
    )
    users_dict = dict([
        (user['user_hash'], user) for user in users_tuple
    ])

    for talk in talks:
        talk['user'] = users_dict[talk['user']]

    return talks

def translate_category(category):
    return dict(CATEGORIES).get(category)


class TalkForm(Form):
    title = TextField(u'Název', validators=[DataRequired()])

    category = RadioField(
        u'Kategorie',
        choices=CATEGORIES,
        validators=[DataRequired()],
    )

    length = RadioField(
        u'Formát',
        choices=[
            # ('22', u'22 minut - volený formát'),
            ('45', u'45 minut - volený formát'),
        ],
        default='45',
        validators=[DataRequired()],
    )

    company = TextField(u'Firma')
    twitter = TextField(u'Twitter')
    web = TextField(u'Web', validators=[Optional(), URL()])
    description = TextField(
        u'Popisek',
        validators=[DataRequired()],
        widget=TextAreaField())
    purpose = TextField(
        u'Pro koho je určena',
        validators=[DataRequired()],
        widget=TextAreaField())

    other = TextField(
        u'Poznámka pro pořadatele',
        widget=TextAreaField()
    )

    video = BooleanField(
        u'Souhlasím se zveřejněním videozáznamu z přednášky',
        default=True)
