# coding: utf-8

from flask_oauth import OAuth
from flask import session, url_for, request, flash, redirect
from login_misc import resolve_user_by_email, create_account
from login_misc import resolve_user_by_twitter
from barcamp import app


@app.route('/login/twitter/')
def login_twitter():
    session['twitter_token'] = None
    return twitter.authorize(
        callback=url_for(
            'login_twitter_authorized',
            next=request.args.get('next')
            or request.referrer
            or None)
    )


@app.route('/login/facebook/')
def login_facebook():
    session['facebook_token'] = None
    return facebook.authorize(
        callback=url_for(
            'login_facebook_authorized',
            next=request.args.get('next')
            or request.referrer
            or url_for('index'),
            _external=True
        )
    )

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=app.config.get('TWITTER_KEY'),
    consumer_secret=app.config.get('TWITTER_SECRET')
)

facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config.get('FACEBOOK_ID'),
    consumer_secret=app.config.get('FACEBOOK_SECRET'),
    request_token_params={'scope': 'email'}
)


@app.route('/login/twitter/process/')
@twitter.authorized_handler
def login_twitter_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(
            u'Bohužel jste neautorizoval aplikaci, '
            u'tudíž Vás nebylo možné přihlásit.', 'warning')
        return redirect(url_for('index'))

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    user_hash = resolve_user_by_twitter(resp['user_id'])
    if not user_hash:
        session['twitter_temp'] = {
            'name': resp['screen_name'],
            'id': resp['user_id']}

        flash(
            u'Váš twitter účet je spárován, '
            u'nyní ještě vyplňte e-mail k dokončení registrace.', 'success')
        return redirect(url_for('login_create_account'))

    session['user_hash'] = user_hash
    flash(u'Úspěšně jste se přihlásil jako %s' % resp['screen_name'])

    return redirect(next_url)


@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@app.route('/login/facebook/process/')
@facebook.authorized_handler
def login_facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    user_hash = resolve_user_by_email(me.data['email'])
    if not user_hash:
        print me.data
        pass
        # pokud ucet neexistuje, vytvorime (a vyplnime) ho z FB
        user_hash = create_account(me.data['email'], None, data={
            'verified': True,
            'name': me.data['name'],
            'location': me.data.get('location', {}).get('name', None),
            'gender': me.data.get('gender', None),
            'bio': me.data.get('bio', None),
        })

    session['user_hash'] = user_hash  # prihlaseni hotovo
    return redirect(request.args.get('next') or url_for('index'))


@facebook.tokengetter
def get_facebook_token(token=None):
    return session.get('facebook_token')
