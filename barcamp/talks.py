# coding: utf-8
import uuid
from collections import defaultdict
from hashlib import md5
from copy import copy

from flask_wtf import Form
from flask import render_template, request, json, flash, redirect
from flask import url_for, abort
from wtforms import TextField, TextAreaField, BooleanField, RadioField, FileField
from wtforms.validators import DataRequired, URL, Optional
from werkzeug.datastructures import CombinedMultiDict

from .barcamp import app
from .login_misc import check_auth, auth_required, get_account, is_admin
from .entrant import user_user_go
from .utils import markdown_markup
from .vote import get_user_votes
from .mailing import send_message_from_template
from .images import square_crop_thumbnail, upload_image


KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
    'account': 'account_%s',
}

CATEGORIES = [
    ('business-marketing', u'Byznys & Marketing'),
    ('design', u'Design'),
    ('inspirational', u'Inspirace'),
    ('development', u'Vývoj, IT & UX'),
]

STATUSES = {
    'new': u'Čeká na schválení',
    'approved': u'Zařazen do hlasování',
    'rejected': u'Téma vyřazeno',
}

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


@app.route('/prednaska/zmenit-stav/<talk_hash>/<status>')
@auth_required
@is_admin
def talk_status(talk_hash, status):
    if status in STATUSES:
        talk_data = get_talk(talk_hash)
        talk_data['status'] = status # zmenime status

        if status == "approve" and 'to_approve' in talk_data:
            talk_data.update(talk_data.get("to_approve", {})) # aplikujeme zmeny

        if 'to_approve' in talk_data:
            del(talk_data['to_approve']) # smazeme zmeny

        app.redis.set(KEYS['talk'] % talk_hash, json.dumps(talk_data))
        return redirect(url_for('talk_detail', talk_hash=talk_hash))
    else:
        abort(404)


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
        form = TalkForm(CombinedMultiDict((request.files, request.form)))
        if form.validate():
            old_hash = talk_hash
            talk_hash = create_or_update_talk(form.data, talk_hash=talk_hash, talk_data=talk_data, need_approvement=need_approvement(talk_data, form.data))
            user_user_go(user_data)
            flash(u'Přednáška byla uložena', 'success')
            if talk_hash != old_hash:
                return redirect(url_for('talk_edit', talk_hash=talk_hash))

    else:
        # show version with things to approve
        talk_data.update(talk_data.get('to_approve', {}))
        form = TalkForm(**talk_data)
    return render_template(
        'talk_form.html',
        informace=markdown_markup('pro-prednasejici'),
        form=form,
        talk=talk_data
    )


def need_approvement(talk_data, talk_form_data):
    return bool(talk_data) and any((
        talk_data['title'] != talk_form_data['title'],
        talk_data['speakers_name'] != talk_form_data['speakers_name'],
        talk_data['category'] != talk_form_data['category'],
        talk_data['description'] != talk_form_data['description'],
        talk_data['purpose'] != talk_form_data['purpose'],
        talk_form_data['image'],
    ))


def extract_things_for_review(talk_hash, talk_form_data):
    data = {
        'title': talk_form_data['title'],
        'speakers_name': talk_form_data['speakers_name'],
        'category': talk_form_data['category'],
        'description': talk_form_data['description'],
        'purpose': talk_form_data['purpose'],
    }

    if 'image' in talk_form_data:
        data['cdn_image'] = extract_image(talk_hash, talk_form_data['image'])
        del(talk_form_data['image'])

    return data

def extract_image(talk_hash, form_data_image):
    if not form_data_image:
        return {}

    uid = uuid.uuid1()
    file_name = f"{talk_hash}-{uid}"
    path = f"/tmp/{file_name}"
    form_data_image.save(path)
    square_crop_thumbnail(path)
    url = upload_image(path, file_name)
    return {
        'cdn_file_name': file_name,
        'url': url,
    }

def fallback_unreviewed_data(new_form_data, old_talk_data):
    new_form_data.update({
        'title': old_talk_data['title'],
        'speakers_name': old_talk_data['speakers_name'],
        'category': old_talk_data['category'],
        'description': old_talk_data['description'],
        'purpose': old_talk_data['purpose'],
    })

def create_or_update_talk(data, talk_hash=None, talk_data=None, need_approvement=False):
    user_data = check_auth()

    if talk_hash is None:
        talk_hash = get_talk_hash(data)
        data['talk_hash'] = talk_hash
        data['status'] = "new"
        data['cdn_image'] = extract_image(talk_hash, data['image'])
        del(data['image'])
        print(data)
        mail_data = copy(data)
        mail_data.update({
            'url': url_for('talk_detail', talk_hash=talk_hash, _external=True)
        })
        mail_data.update(user_data)
        # send talk mail
        flash(u'Nové přednášky schvalujeme do 3 dnů.', 'info')
        send_message_from_template(
            app.config['TALK_NOTIFICATION_MAIL'],
            u"Nová přednáška - nutno schválit: %s" % data['title'],
            "data/new-talk.md",
            mail_data,
            from_email=user_data['email'],
            from_name=user_data['name'],
        )
    else:
        data['status'] = talk_data['status']
        data['cdn_image'] = talk_data.get('cdn_image', {})
        mail_data = copy(data)
        mail_data.update({
            'url': url_for('talk_detail', talk_hash=talk_hash, _external=True)
        })
        mail_data.update(user_data)

        subject = u"Změněná přednáška - bez schválení: %s" % data['title']
        if need_approvement:
            subject = u"Změněná přednáška - nutno schválit: %s" % data['title']
            data['to_approve'] = extract_things_for_review(talk_hash, data)
            mail_data.update(data['to_approve'])
            fallback_unreviewed_data(data, talk_data)
            flash(u'Změny přednášek viditelné na webu schvalujeme do 3 dnů', 'info')
        else:
            del(data['image'])

        send_message_from_template(
            app.config['TALK_NOTIFICATION_MAIL'],
            subject,
            "data/new-talk.md",
            mail_data,
            from_email=user_data['email'],
            from_name=user_data['name'],
        )

    data.update({
        'user': user_data['user_hash'],
        'talk_hash': talk_hash,
    })

    app.redis.set(KEYS['talk'] % talk_hash, json.dumps(data))
    # zalozime hlasovani - bezpecne pres zincrby (namisto zadd s if podminkou)
    app.redis.zincrby(KEYS['talks'], 0, talk_hash)
    return talk_hash


def get_talk_hash(data, depth=5):
    "Non-colide talk hash algoritm ;)"
    talk_hash = md5(f"{data['title']}|{depth}".encode()).hexdigest()[:8]
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

    talks = list(filter(
        lambda x: bool(x),
        map(
            lambda talk: json.loads(talk or 'false'),
            app.redis.mget(map(lambda key: KEYS['talk'] % key, talk_hashes))
        )
    ))
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

def translate_status(status):
    return dict(STATUSES).get(status)


class TalkForm(Form):
    title = TextField(u'Název', validators=[DataRequired()])
    speakers_name = TextField(u'Jméno řečníka (řečníků)', validators=[DataRequired()])
    contact_phone = TextField(u'Telefonní  číslo (neveřejná informace)', validators=[DataRequired()])
    image = FileField(u'Portrét řečníka (čtverec)')

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

    description = TextField(
        u'Popisek',
        validators=[DataRequired()],
        widget=TextAreaField())

    purpose = TextField(
        u'Pro koho je určena',
        validators=[DataRequired()],
        widget=TextAreaField())

    other = TextField(
        u'Poznámka pro pořadatele (neveřejná informace)',
        widget=TextAreaField()
    )
