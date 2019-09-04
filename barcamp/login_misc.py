# coding: utf-8

from functools import wraps
from flask import abort, session, request, redirect, flash, url_for, json
from .barcamp import app
from hashlib import md5, sha1
import mailchimp
from datetime import datetime
from sentry_sdk import capture_exception

KEYS = {
    'account': 'account_%s',
    'email': 'email_%s',
    'gdpr': 'gdpr_consent_%s_v2' % app.config['YEAR'],
    'gdpr_date': 'gdpr_consent_date_%s' % app.config['YEAR'],
}


def login_redirect():
    path = request.path
    flash(
        u"Stránka [%s] je dostupná jen přihlášenému uživateli" % path,
        "warning")
    # session['next'] = path
    return redirect(url_for('login'))


def authorized_redirect(url):
    user = check_auth(skip_gdpr_check=True)

    if user and gdpr_consent_required(user):
        return gdpr_redirect()

    return redirect(url)


def gdpr_redirect():
    path = request.path
    flash(
        u"Potřebujeme doplnit souhlas se zpracováním osobních údajů",
        "warning")
    # session['next'] = path
    return redirect(url_for('gdpr_consent'))


def auth_required(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        user = check_auth(skip_gdpr_check=True)
        if not user:
            session.clear()
            return login_redirect()

        if gdpr_consent_required(user):
            return gdpr_redirect()
        return fn(*args, **kwargs)

    return wrap


def is_admin(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not check_admin():
            abort(418)

        return fn(*args, **kwargs)

    return wrap


def check_admin():
    user = check_auth(skip_gdpr_check=True)
    return user and (user['email'] == u'petr@joachim.cz' or user['email'].endswith('@barcampbrno.cz'))


def check_auth(skip_gdpr_check=False):
    user_hash = session.get('user_hash', None)
    user = get_account(user_hash)
    if not skip_gdpr_check and gdpr_consent_required(user):
        return False
    return user


def get_account(user_hash):
    return json.loads(app.redis.get(KEYS['account'] % user_hash) or "false")


def create_update_profile(data, user_hash=None):
    if not user_hash:
        user_hash = get_user_hash(data)
        data['user_hash'] = user_hash
    else:
        new_data = get_account(user_hash)
        new_data.update(data)
        data = new_data

    app.redis.set(KEYS['account'] % user_hash, json.dumps(data))
    return user_hash


def get_user_hash(data, depth=5):
    "Non-colide user hash algoritm ;)"
    user_hash = md5(f"{data['email']}|depth".encode()).hexdigest()[:8]
    if not app.redis.setnx(KEYS['account'] % user_hash, 'false'):
        return get_user_hash(data, depth - 1)

    return user_hash


def update_password(user_hash, email, password=None):
    email = email.lower()
    if password is not None:
        password = sha1(password.encode()).hexdigest()
    app.redis.set(
        KEYS['email'] % email,
        json.dumps({
            'user_hash': user_hash,
            'password': password
        }))


def resolve_user_by_email(email, password=None):
    """
        Return user ID from email address
        also validates password, if provided
    """
    email = email.lower()
    data = json.loads(app.redis.get(KEYS['email'] % email) or "false")
    if data:
        #check password
        if password and\
                sha1(password.encode()).hexdigest() != data.get('password', None):
            return False  # password did not match
        return data['user_hash']  # only if everything is OK
    return False  # email not found


def gdpr_consent_required(user):
    if not user:
        return False

    return not (KEYS['gdpr'] in user and user[KEYS['gdpr']])


def create_account(email, password, user_hash=None, data=None):
    data = data or {}

    data.update({'email': email})#, 'password': password})
    email = email.lower()
    user_hash = create_update_profile(data)
    update_password(user_hash, email, password)

    return user_hash


def store_gdpr_consent(user):
    api = mailchimp.Mailchimp(app.config['MAILCHIMP_API_KEY'])
    try:
        api.lists.subscribe(
            app.config['MAILCHIMP_LIST_ID'],
            {'email': user['email']},
            merge_vars={'ROK': app.config['YEAR']},
            double_optin=False,
            update_existing=True,
            send_welcome=True
        )
    except Exception as e:
        capture_exception(e)

    create_update_profile(
        {
            KEYS['gdpr']: True,
            KEYS['gdpr_date']: str(datetime.now())
        },
        user['user_hash']
    )

    flash(u'Souhlas byl uložen', 'success')
