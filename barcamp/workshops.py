# coding: utf-8
from barcamp import app
from flask import render_template, request, json, flash, redirect
from flask import url_for, abort
from login_misc import check_auth, auth_required, get_account
from entrant import user_user_go
from flask_wtf import Form
from wtforms import TextField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, URL, Optional
from hashlib import md5
from utils import markdown_markup, send_feedback_mail

KEYS = {
    'workshop': 'workshop_%s_%%s' % app.config['YEAR'],
    'workshops': 'workshops_%s' % app.config['YEAR'],
    'account': 'account_%s',
}

def workshopy():
    return [{"workshop_hash": key} for key in app.redis.zrange(KEYS['workshops'], 0, -1)]

@app.route('/%s/workshop/<workshop_hash>.html' % app.config['YEAR'], generator=workshopy)
def workshop_detail(workshop_hash):
    workshop = get_workshop(workshop_hash)
    if not workshop:
        abort(404)

    author = get_account(workshop['user'])

    return render_template(
        'workshop_detail.html',
        workshop=workshop,
        author=author
    )


@app.route('/workshop/odstranit/<workshop_hash>/')
@auth_required
def workshop_delete(workshop_hash):
    workshop_data = get_workshop(workshop_hash)
    user_data = check_auth()

    if user_data['user_hash'] != workshop_data['user']:
        abort(403)  # uzivatel nema pravo

    app.redis.delete(KEYS['workshop'] % workshop_hash)
    app.redis.zrem(KEYS['workshops'], workshop_hash)
    flash(u'Workshop byl smazán', 'success')
    return redirect(url_for('index'))


@app.route(
    "/workshop/pridat/",
    methods=['GET', 'POST'],
    defaults={'workshop_hash': None})
@app.route("/workshop/editace/<workshop_hash>/", methods=['GET', 'POST'])
@auth_required
def workshop_edit(workshop_hash=None):
    workshop_data = {}
    user_data = check_auth()
    if workshop_hash:
        workshop_data = get_workshop(workshop_hash)

        if user_data['user_hash'] != workshop_data['user']:
            abort(403)  # uzivatel tohle nemuze editovat

    if request.method == "POST":
        form = WorkshopForm(request.form)
        if form.validate():
            old_hash = workshop_hash
            workshop_hash = create_or_update_workshop(form.data, workshop_hash)
            user_user_go(user_data)
            flash(u'Workshop byl uložen', 'success')
            if workshop_hash != old_hash:
                return redirect(url_for('workshop_edit', workshop_hash=workshop_hash))
    else:
        form = WorkshopForm(**workshop_data)
    return render_template(
        'workshop_form.html',
        informace=markdown_markup('pro-workshopisty'),
        form=form,
        workshop=workshop_data
    )


def create_or_update_workshop(data, workshop_hash=None):
    user_data = check_auth()
    if workshop_hash is None:
        workshop_hash = get_workshop_hash(data)
        data['workshop_hash'] = workshop_hash
        data['status'] = 'waiting'
        # send workshop mail
        send_feedback_mail(
            u"Nový workshop: %s" % data['title'],
            "data/new-workshop.md",
            data,
            user_data,
            url_for(
                'workshop_detail',
                workshop_hash=workshop_hash,
                _external=True
            )
        )

    data.update({
        'user': user_data['user_hash'],
        'workshop_hash': workshop_hash,
    })

    app.redis.set(KEYS['workshop'] % workshop_hash, json.dumps(data))
    # zalozime hlasovani - bezpecne pres zincrby (namisto zadd s if podminkou)
    app.redis.zincrby(KEYS['workshops'], workshop_hash, 0)
    return workshop_hash


def get_workshop_hash(data, depth=5):
    "Non-colide workshop hash algoritm ;)"
    workshop_hash = md5("%s|%s" % (json.dumps(data), depth)).hexdigest()[:8]
    if not app.redis.setnx(KEYS['workshop'] % workshop_hash, 'false'):
        return get_workshop_hash(data, depth - 1)

    return workshop_hash


def get_workshop(workshop_hash):
    return json.loads(app.redis.get(KEYS['workshop'] % workshop_hash) or 'false')


def get_workshops(user_hash=None):

    return _get_workshops();


def get_workshops_dict():
    workshops = _get_workshops()
    return dict([(workshop['workshop_hash'], workshop) for workshop in workshops])


def _get_workshops():
    workshop_tuples = app.redis.zrevrange(KEYS['workshops'], 0, -1, withscores=True)
    workshop_hashes = [workshop_tuple[0] for workshop_tuple in workshop_tuples]
    workshop_scores = dict(workshop_tuples)

    if not workshop_hashes:
        return []

    workshops = map(
        lambda workshop: json.loads(workshop or 'false'),
        app.redis.mget(map(lambda key: KEYS['workshop'] % key, workshop_hashes))
    )
    try:
        workshops.remove(False)
        workshops.remove(False)
        workshops.remove(False)
        workshops.remove(False)
        workshops.remove(False)
    except:
        pass

    map(
        lambda workshop: workshop.update({
            'score': int(workshop_scores.get(workshop['workshop_hash']) or 0),
            'status': 'waiting',
        }),
        workshops
    )

    user_hashes = [workshop['user'] for workshop in workshops]
    users_tuple = map(
        lambda user: json.loads(user or 'false'),
        app.redis.mget(map(lambda key: KEYS['account'] % key, user_hashes))
    )
    users_dict = dict([
        (user['user_hash'], user) for user in users_tuple
    ])

    for workshop in workshops:
        workshop['user'] = users_dict[workshop['user']]

    return workshops


def translate_status(status):
    return {
        'waiting': u'Čeká na schválení',
        'approved': u'Schválen',
        'disapproved': u'Neschválen',
    }[status]


class WorkshopForm(Form):
    title = TextField(u'Název', validators=[DataRequired()])
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

    needs = TextField(
        u'Požadavky na účastníky',
        validators=[Optional()],
        widget=TextAreaField())

    other = TextField(
        u'Poznámka pro pořadatele',
        widget=TextAreaField()
    )

    minutes = IntegerField(
        u'Trvání (minuty)',
        default=115)

    max_count = IntegerField(
        u'Počet účastníků',
        default=30)
