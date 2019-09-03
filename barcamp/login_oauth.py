# coding: utf-8

from flask_dance.contrib.facebook import facebook, make_facebook_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.contrib.linkedin import linkedin, make_linkedin_blueprint
from flask_dance.consumer import oauth_authorized
from flask import session, url_for, request, flash, redirect
from .login_misc import resolve_user_by_email, create_account, authorized_redirect
from .barcamp import app

@app.route('/connect/facebook')
def connect_facebook():
    next = session.get('next', None)
    resp = facebook.get('/me?fields=id,name,email')
    data = resp.json()

    if not data.get('email'):
        flash(u'Nepodařilo se získat e-mail z Facebooku, zkuste to znovu.', 'danger')
        return redirect(url_for('login'))

    user_hash = resolve_user_by_email(data['email'])
    new_account = False
    if not user_hash:
        # pokud ucet neexistuje, vytvorime (a vyplnime) ho z FB
        user_hash = create_account(data['email'], None, data={
            'verified': True,
            'name': data['name'],
        })

        new_account = True

    session['user_hash'] = user_hash  # prihlaseni hotovo

    if new_account:
        flash(u'Váš Facebook účet je spárován', 'success')

    session['next'] = None
    return authorized_redirect(next or url_for('login_settings'))


facebook_blueprint = make_facebook_blueprint(
    client_id=app.config['FACEBOOK_ID'],
    client_secret=app.config['FACEBOOK_SECRET'],
    scope="email",
    rerequest_declined_permissions=True,
    redirect_to='connect_facebook'
)
app.register_blueprint(facebook_blueprint, url_prefix='/login/oauth')

@app.route('/connect/google')
def connect_google():
    next = session.get('next', None)
    resp = google.get("/oauth2/v1/userinfo")
    data = resp.json()

    if not data.get('email'):
        flash(u'Nepodařilo se získat e-mail z Google, zkuste to znovu.', 'danger')
        return redirect(url_for('login'))

    user_hash = resolve_user_by_email(data['email'])
    new_account = False
    if not user_hash:
        # pokud ucet neexistuje, vytvorime (a vyplnime) ho z FB
        user_hash = create_account(data['email'], None, data={
            'verified': True,
            'name': data.get('name', ''),
        })

        new_account = True
    session['user_hash'] = user_hash  # prihlaseni hotovo
    if new_account:
        flash(u'Váš Google účet je spárován', 'success')

    session['next'] = None
    return authorized_redirect(next or url_for('login_settings'))

google_blueprint = make_google_blueprint(
    client_id = app.config['GOOGLE_ID'],
    client_secret = app.config['GOOGLE_SECRET'],
    scope="openid https://www.googleapis.com/auth/userinfo.email",
    redirect_to="connect_google"
)
app.register_blueprint(google_blueprint, url_prefix='/login/oauth')


@app.route('/connect/linkedin')
def connect_linkedin():
    next = session.get('next', None)
    resp = linkedin.get("/v2/me")
    data = resp.json()

    1/0

    if not data.get('email'):
        flash(u'Nepodařilo se získat e-mail z Linkedin, zkuste to znovu.', 'danger')
        return redirect(url_for('login'))

    user_hash = resolve_user_by_email(data['email'])
    new_account = False
    if not user_hash:
        # pokud ucet neexistuje, vytvorime (a vyplnime) ho z FB
        user_hash = create_account(data['email'], None, data={
            'verified': True,
            'name': data.get('name', ''),
        })

        new_account = True
    session['user_hash'] = user_hash  # prihlaseni hotovo
    if new_account:
        flash(u'Váš Linkedin účet je spárován', 'success')

    session['next'] = None
    return authorized_redirect(next or url_for('login_settings'))

linkedin_blueprint = make_linkedin_blueprint(
    client_id = app.config['LINKEDIN_ID'],
    client_secret = app.config['LINKEDIN_SECRET'],
    scope="email",
    redirect_to="connect_linkedin"
)
app.register_blueprint(linkedin_blueprint, url_prefix="/login/oauth")
