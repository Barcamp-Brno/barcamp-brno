# coding: utf-8

from flask import render_template, session, redirect, flash
from flask import url_for, request, json
from barcamp import app
from flask_oauth import OAuth
from functools import wraps
from hashlib import md5
from flask_wtf import Form, TextField, Required, Email
import base64

KEYS = {
    'account': 'account_%s',
    'email': 'email_%s',
    'twitter': 'twitter_%s',
}


def auth_required(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not session.get('user_hash', False):
            path = request.path
            flash(
                u"Stránka [%s] je dostupná jen přihlášenému uživateli" % path,
                "warning")
            return redirect(url_for('login', next=path))
        return fn(*args, **kwargs)

    return wrap


@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            user_hash = resolve_user_by_email(
                form.data.get('email'),
                form.data.get('password'))
            if not user_hash:
                session['default_email'] = form.data.get('email')
                flash(
                    u'Neplatná kombinace e-mailu a hesla, zkuste to znovu.',
                    'warning')
            else:
                session['user_hash'] = user_hash

    else:
        form = LoginForm()

    if check_auth():
        #TODO redirect for "next_url :)"
        flash(u'Nyní jste přihlášen', 'success')
        return redirect(url_for('login_settings'))

    return render_template("login.html", form=form)


@app.route("/nastaveni-profilu/")
@auth_required
def login_settings():
    #TODO formular na ukladani detailu uzivatele
    return render_template('nastaveni.html', user=check_auth())


@app.route("/logout/")
def logout():
    session.clear()
    flash(u'Nyní jste odhlášen', 'success')
    return redirect(url_for('index'))


@app.route('/login/registrace/zalozeni-uctu/', methods=['GET', 'POST'])
def login_create_account():
    if request.method == "POST":
        form = EmailForm(request.form)
        if form.validate():
            email = form.data.get('email').lower()
            user_hash = resolve_user_by_email(email)
            if user_hash:
                flash(
                    u'Účet s tímto e-mailem již existuje, '
                    u'chcete obnovit zapomenuté heslo?',
                    'warning')
                return redirect(url_for(
                    'login_forgotten_password',
                    email=email))
            # TODO send email
            email = base64.b64encode(email)
            token = md5("%s|%s" % (app.secret_key, email)).hexdigest()
            url = url_for(
                'login_click_from_email',
                token=token,
                email=email,
                _external=True)
            flash("tohle poslu mailem - %s " % url, 'debug')
            return redirect(url_for('login_email_verify'))
    else:
        form = EmailForm()
    return render_template('login_create_account.html', form=form)


@app.route("/login/registrace/overeni-emailu/")
def login_email_verify():
    return render_template('login_email_verify.html')


@app.route("/login/registrace/odkaz-z-mailu/")
def login_click_from_email():
    email = request.args.get('email', None)
    token = request.args.get('token', None)

    if token == md5("%s|%s" % (app.secret_key, email)).hexdigest():
        email = base64.b64decode(email)
        session['verified-mail'] = email
        return redirect(url_for('login_basic_data'))
    flash(
        u'Platnost odkazu již vypršela, nebo je odkaz v nespárvném tvaru',
        'warning')
    return redirect(url_for('login_create_account'))


@app.route("/login/registrace/vyplneni-udaju/", methods=['GET', 'POST'])
def login_basic_data():
    if request.method == 'POST':
        form = BasicForm(request.form)
        if form.validate():
            email = session.get('verified-mail')
            fullname = form.data.get('fullname')
            password = form.data.get('password')
            user_hash = create_account(email, password, data={
                'name': fullname,
            })
            session.clear()
            session['user_hash'] = user_hash
            return redirect(url_for('login_settings'))
    else:
        form = BasicForm()
    return render_template('login_basic_data.html', form=form)


@app.route("/login/zapomenute-heslo/", methods=['POST', 'GET'])
def login_forgotten_password():
    if request.method == "POST":
        form = EmailForm(request.form)
        if form.validate():
            email = form.data.get('email')
            # TODO send mail
            email = base64.b64encode(email)
            token = md5("%s|%s" % (app.secret_key, email)).hexdigest()
            url = url_for(
                'login_click_from_email_password',
                token=token,
                email=email,
                _external=True)
            flash("tohle poslu mailem - %s " % url, 'debug')
            return redirect(url_for('login_forgotten_verify'))
    else:
        form = EmailForm(request.args)

    return render_template('login_forgotten_password.html')


@app.route("/login/resetovat-heslo/overeni-emailu/")
def login_forgotten_verify():
    return render_template('login_forgotten_verify.html')


@app.route("/login/resetovat-heslo/odkaz/", methods=['GET', 'POST'])
def login_click_from_email_password():
    email = request.args.get('email', None)
    token = request.args.get('token', None)

    if token == md5("%s|%s" % (app.secret_key, email)).hexdigest():
        email = base64.b64decode(email)
        return "email byl %s" % email
        # TODO redirect na stranku s vyreserovanim hesla
        # TODO ulozit mail do session
    flash(
        u'Platnost odkazu již vypršela, nebo je odkaz v nespárvném tvaru',
        'warning')
    return redirect(url_for('login_forgotten_password'))


@app.route('/login/resetovat-heslo/')
def login_reset_password():
    pass


def check_auth():
    user_hash = session.get('user_hash', None)
    return get_account(user_hash)


def get_account(user_hash):
    return json.loads(app.redis.get(KEYS['account'] % user_hash) or "false")


def create_update_profile(data, user_hash=None):
    if not user_hash:
        user_hash = md5(json.dumps(data)).hexdigest()[:8]
        data['user_hash'] = user_hash
        # TODO check for collisions

    app.redis.set(KEYS['account'] % user_hash, json.dumps(data))
    return user_hash


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
                md5(password).hexdigest() != data.get('password', None):
            return False  # password did not match
        return data['user_hash']  # only if everything is OK
    return False  # email not found


def resolve_user_by_twitter(twitter_id):
    return app.redis.get(KEYS['twitter'] % twitter_id) or False


def create_account(email, password, user_hash=None, data=None):
    data = data or {}
    if password is not None:
        password = md5(password).hexdigest()
    data.update({'email': email, 'password': password})
    email = email.lower()
    user_hash = create_update_profile(data)
    app.redis.set(
        KEYS['email'] % email,
        json.dumps({
            'user_hash': user_hash,
            'password': password
        }))

    return user_hash


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


### FORMS ###
class LoginForm(Form):
    email = TextField('E-mail', validators=[Required(), Email()])
    password = TextField('Heslo', validators=[Required()])


class EmailForm(Form):
    email = TextField('E-mail', validators=[Required(), Email()])


class BasicForm(Form):
    fullname = TextField(u'Jméno', validators=[Required()])
    password = TextField('Heslo', validators=[Required()])


### OAUTH SPECIFIC ###
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
    #session['twitter_user'] = resp['screen_name']
    print resp

    flash(u'Úspěšně jste se přihlásil jako %s' % resp['screen_name'])
    # TODO: zkontrolovat, jestli k twitteru existuje ucet,
    #       jinak vynutit registraci

    # TODO (ulozit udaje do session, abychom se neptali vickrat
    #       - udela se jen overeni mailu)
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
