# coding: utf-8
from barcamp import app
from flask import render_template, request, json, flash, redirect
from flask import url_for, abort
from login_misc import check_auth, auth_required, get_account
from flask_wtf import Form, TextField, Required, TextArea, URL, Optional
from hashlib import md5
from utils import menu

KEYS = {
    'talk': 'talk_%s',
    'talks': 'talks',
}


@app.route('/prednaska/<talk_hash>/')
def talk_detail(talk_hash):
    talk = get_talk(talk_hash)
    if not talk:
        abort(404)

    author = get_account(talk['user'])

    return render_template(
        'talk_detail.html',
        talk=talk,
        menu=menu(),
        author=author,
        user=check_auth())


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
    if talk_hash:
        talk_data = get_talk(talk_hash)
        user_data = check_auth()

        if user_data['user_hash'] != talk_data['user']:
            abort(403)  # uzivatel tohle nemuze editovat

    if request.method == "POST":
        form = TalkForm(request.form)
        if form.validate():
            old_hash = talk_hash
            talk_hash = create_or_update_talk(form.data, talk_hash)
            flash(u'Přednáska byla uložena', 'success')
            if talk_hash != old_hash:
                return redirect(url_for('talk_edit', talk_hash=talk_hash))
    else:
        form = TalkForm(**talk_data)
    return render_template(
        'talk_form.html',
        form=form, user=check_auth(), talk=talk_data, menu=menu())


def create_or_update_talk(data, talk_hash=None):
    user_data = check_auth()
    print data
    if talk_hash is None:
        talk_hash = get_talk_hash(data)
        data['talk_hash'] = talk_hash

    data.update({
        'user': user_data['user_hash'],
        'talk_hash': talk_hash,
    })

    app.redis.set(KEYS['talk'] % talk_hash, json.dumps(data))
    if not app.redis.zrank(KEYS['talks'], talk_hash):
        app.redis.zadd(KEYS['talks'], talk_hash, 0)
    return talk_hash


def get_talk_hash(data, depth=5):
    "Non-colide talk hash algoritm ;)"
    talk_hash = md5("%s|%s" % (json.dumps(data), depth)).hexdigest()[:8]
    if not app.redis.setnx(KEYS['talk'] % talk_hash, 'false'):
        return get_talk_hash(data, depth - 1)

    return talk_hash


def get_talk(talk_hash):
    return json.loads(app.redis.get(KEYS['talk'] % talk_hash) or 'false')


def get_talks(user_hash=None):
    talk_tuples = app.redis.zrevrange(KEYS['talks'], 0, -1, withscores=True)
    talk_hashes = [talk_tuple[0] for talk_tuple in talk_tuples]
    talk_scores = dict(talk_tuples)

    if not talk_hashes:
        return []

    talks = map(
        lambda talk: json.loads(talk or 'false'),
        app.redis.mget(map(lambda key: KEYS['talk'] % key, talk_hashes))
    )
    map(
        lambda talk: talk.update(
            {'score': int(talk_scores.get(talk['talk_hash']) or 0)}),
        talks
    )

    user_hashes = [talk['user'] for talk in talks]
    users_tuple = map(
        lambda user: json.loads(user or 'false'),
        app.redis.mget(map(lambda key: 'account_%s' % key, user_hashes))
    )
    users_dict = dict([
        (user['user_hash'], user) for user in users_tuple
    ])

    for talk in talks:
        talk['user'] = users_dict[talk['user']]

    return talks


class TalkForm(Form):
    title = TextField(u'Název', validators=[Required()])
    company = TextField(u'Firma')
    twitter = TextField(u'Twitter')
    web = TextField(u'Web', validators=[Optional(), URL()])
    description = TextField(
        u'Popisek',
        validators=[Required()],
        widget=TextArea())
    purpose = TextField(
        u'Pro koho je určena',
        validators=[Required()],
        widget=TextArea())

    other = TextField(
        u'Poznámka pro pořadatele',
        widget=TextArea()
    )
