# coding: utf-8

from flask_dance.contrib.facebook import facebook, make_facebook_blueprint
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
        flash(u'Váš facebook účet je spárován', 'success')

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
