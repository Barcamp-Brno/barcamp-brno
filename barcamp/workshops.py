# coding: utf-8
import uuid
from copy import copy
from .barcamp import app
from flask import render_template, request, json, flash, redirect
from flask import url_for, abort
from .login_misc import check_auth, auth_required, get_account, is_admin
from .entrant import user_user_go
from flask_wtf import Form
from wtforms import TextField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, URL, Optional
from werkzeug.datastructures import CombinedMultiDict
from hashlib import md5
from .utils import markdown_markup
from .mailing import send_message_from_template
from .images import square_crop_thumbnail, upload_image

KEYS = {
    'workshop': 'workshop_%s_%%s' % app.config['YEAR'],
    'workshops': 'workshops_%s' % app.config['YEAR'],
    'account': 'account_%s',
}

STATUSES = {
    'waiting': u'Čeká na schválení',
    'approved': u'Zařazen do programu',
    'rejected': u'Nezařazen do programu',
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


@app.route('/workshop/zmenit-stav/<workshop_hash>/<status>')
@auth_required
@is_admin
def workshop_status(workshop_hash, status):
    if status in STATUSES:
        workshop_data = get_workshop(workshop_hash)
        workshop_data['status'] = status

        if status == "approved" and 'to_approve' in workshop_data:
            if workshop_data.get('to_approve', {}).get('cdn_image') == {}:
                del(workshop_data['to_approve']['cdn_image'])

            workshop_data.update(workshop_data.get("to_approve", {})) # aplikujeme zmeny

        if 'to_approve' in workshop_data:
            del(workshop_data['to_approve']) # smazeme zmeny

        app.redis.set(KEYS['workshop'] % workshop_hash, json.dumps(workshop_data))
        return redirect(url_for('workshop_detail', workshop_hash=workshop_hash))
    else:
        abort(404)


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
        form = WorkshopForm(CombinedMultiDict((request.files, request.form)))
        if form.validate():
            old_hash = workshop_hash
            workshop_hash = create_or_update_workshop(
                form.data,
                workshop_hash=workshop_hash,
                workshop_data=workshop_data,
                need_approvement=need_approvement(workshop_data, form.data)
            )
            user_user_go(user_data)
            flash(u'Workshop byl uložen', 'success')
            if workshop_hash != old_hash:
                return redirect(url_for('workshop_edit', workshop_hash=workshop_hash))
    else:
        # show version with things to approve
        workshop_data.update(workshop_data.get('to_approve', {}))
        form = WorkshopForm(**workshop_data)
    return render_template(
        'workshop_form.html',
        informace=markdown_markup('pro-workshopisty'),
        form=form,
        workshop=workshop_data
    )


def need_approvement(workshop_data, workshop_form_data):
    return bool(workshop_data) and any((
        workshop_data['title'] != workshop_form_data['title'],
        workshop_data['speakers_name'] != workshop_form_data['speakers_name'],
        workshop_data['description'] != workshop_form_data['description'],
        workshop_data['purpose'] != workshop_form_data['purpose'],
        workshop_data['needs'] != workshop_form_data['needs'],
        workshop_form_data['image'],
    ))


def extract_things_for_review(workshop_hash, workshop_form_data):
    data = {
        'title': workshop_form_data['title'],
        'speakers_name': workshop_form_data['speakers_name'],
        'description': workshop_form_data['description'],
        'purpose': workshop_form_data['purpose'],
        'needs': workshop_form_data['needs'],
    }

    if 'image' in workshop_form_data:
        data['cdn_image'] = extract_image(workshop_hash, workshop_form_data['image'])
        del(workshop_form_data['image'])

    return data

def extract_image(workshop_hash, form_data_image):
    if not form_data_image:
        return {}

    uid = uuid.uuid1()
    file_name = f"{workshop_hash}-{uid}"
    path = f"/tmp/{file_name}"
    form_data_image.save(path)
    square_crop_thumbnail(path)
    url = upload_image(path, file_name)
    return {
        'cdn_file_name': file_name,
        'url': url,
    }

def fallback_unreviewed_data(new_form_data, old_workshop_data):
    new_form_data.update({
        'title': old_workshop_data['title'],
        'speakers_name': old_workshop_data['speakers_name'],
        'description': old_workshop_data['description'],
        'purpose': old_workshop_data['purpose'],
        'needs': old_workshop_data['needs'],
    })


def create_or_update_workshop(data, workshop_hash=None, workshop_data=None, need_approvement=False):
    user_data = check_auth()
    if workshop_hash is None:
        workshop_hash = get_workshop_hash(data)
        data['workshop_hash'] = workshop_hash
        data['status'] = 'waiting'
        data['cdn_image'] = extract_image(workshop_hash, data['image'])
        del(data['image'])
        # send workshop mail
        mail_data = copy(data)
        mail_data.update({
            'url': url_for('workshop_detail', workshop_hash=workshop_hash, _external=True)
        })
        mail_data.update(user_data)

        flash(u'Nové workshopy schvalujeme do 3 dnů.', 'info')
        send_message_from_template(
            app.config['TALK_NOTIFICATION_MAIL'],
            u"Nový workshop - nutno schválit: %s" % data['title'],
            "data/new-workshop.md",
            mail_data,
            from_email=user_data['email'],
            from_name=user_data['name'],
        )
    else:
        data['status'] = workshop_data['status']
        data['cdn_image'] = workshop_data.get('cdn_image', {})
        mail_data = copy(data)
        mail_data.update({
            'url': url_for('workshop_detail', workshop_hash=workshop_hash, _external=True)
        })
        mail_data.update(user_data)

        subject = u"Změněný workshop - bez schválení: %s" % data['title']
        if need_approvement:
            subject = u"Změněný workshop - nutno schválit: %s" % data['title']
            data['to_approve'] = extract_things_for_review(workshop_hash, data)
            mail_data.update(data['to_approve'])
            fallback_unreviewed_data(data, workshop_data)
            flash(u'Změny workshopů viditelné na webu schvalujeme do 3 dnů', 'info')
        else:
            del(data['image'])

        send_message_from_template(
            app.config['TALK_NOTIFICATION_MAIL'],
            subject,
            "data/new-workshop.md",
            mail_data,
            from_email=user_data['email'],
            from_name=user_data['name'],
        )

    data.update({
        'user': user_data['user_hash'],
        'workshop_hash': workshop_hash,
    })

    app.redis.set(KEYS['workshop'] % workshop_hash, json.dumps(data))
    # zalozime hlasovani - bezpecne pres zincrby (namisto zadd s if podminkou)
    app.redis.zincrby(KEYS['workshops'], 0, workshop_hash)
    return workshop_hash


def get_workshop_hash(data, depth=5):
    "Non-colide workshop hash algoritm ;)"
    workshop_hash = md5(f"{data['title']}|{depth}".encode()).hexdigest()[:8]
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

    workshops = list(filter(
        lambda x: bool(x),
        map(
            lambda workshop: json.loads(workshop or 'false'),
            app.redis.mget(map(lambda key: KEYS['workshop'] % key, workshop_hashes))
        )
    ))
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
    return STATUSES[status or 'waiting']


class WorkshopForm(Form):
    title = TextField(u'Název', validators=[DataRequired()])
    speakers_name = TextField(u'Jméno řečníka (řečníků)', validators=[DataRequired()])
    contact_phone = TextField(u'Telefonní  číslo (neveřejná informace)', validators=[DataRequired()])
    image = FileField(u'Portrét řečníka (čtverec)')
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
