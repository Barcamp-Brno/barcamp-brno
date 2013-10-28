# coding: utf-8

from flask import render_template, session, redirect, flash
from flask import url_for, request, abort
from barcamp import app
from hashlib import md5
from wtforms import Form, TextField
from wtforms.validators import Required, Email, EqualTo
import base64
from login_misc import auth_required, resolve_user_by_email
from login_misc import check_auth, create_account, register_twitter
from login_misc import update_password, create_update_profile
from views import menu
import markdown
from flask.ext.mail import Mail, Message

KEYS = {
    'account': 'account_%s',
    'email': 'email_%s',
    'twitter': 'twitter_%s',
}


@app.route("/login/", methods=['GET', 'POST'])
def login():
    next = session.get('next', None)
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
                session.clear()
                session['user_hash'] = user_hash

    else:
        form = LoginForm()

    if check_auth():
        flash(u'Nyní jste přihlášen', 'success')
        return redirect(next or url_for('login_settings'))

    return render_template("login.html", form=form, menu=menu())


@app.route("/nastaveni-profilu/", methods=['GET', 'POST'])
@auth_required
def login_settings():
    user = check_auth()
    if request.method == "POST":
        form = SettingsForm(request.form)
        if form.validate():
            create_update_profile(form.data, user['user_hash'])
            flash(u'Profil aktualizován', 'success')
            return redirect(url_for('login_settings'))
    else:
        form = SettingsForm(**user)
    return render_template('nastaveni.html', user=user, form=form, menu=menu())


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
            raw_email = email
            email = base64.b64encode(email)
            token = md5("%s|%s" % (app.secret_key, email)).hexdigest()
            url = url_for(
                'login_click_from_email',
                token=token,
                email=email,
                _external=True)

            if app.debug:
                flash(url, "debug")

            send_mail(
                u'Vytvoření účtu',
                raw_email,
                "data/verify-account.md",
                url)
            return redirect(url_for('login_email_verify'))
    else:
        form = EmailForm()
    return render_template('login_create_account.html', form=form, menu=menu())


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
        twitter_data = session.get('twitter_temp', None)
        if twitter_data:
            user_data = {
                'name': twitter_data['name'],
                'twitter_id': twitter_data['id'],
            }
            user_hash = create_account(email, None, data=user_data)
            register_twitter(twitter_data['id'], user_hash)
            next = session.get('next', None)
            session.clear()
            session['user_hash'] = user_hash
            flash(u'Váš účet je vytvořen a spárován s twitterem')
            return redirect(next or url_for('login_settings'))
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
            next = session.get('next', None)
            session.clear()
            session['user_hash'] = user_hash
            flash(u'Nyní jste přihlášen', 'success')
            return redirect(next or url_for('login_settings'))
    else:
        form = BasicForm()
    return render_template('login_basic_data.html', form=form, menu=menu())


@app.route("/login/zapomenute-heslo/", methods=['POST', 'GET'])
def login_forgotten_password():
    if request.method == "POST":
        form = EmailForm(request.form)
        if form.validate():
            email = form.data.get('email')
            if not resolve_user_by_email(email):
                flash(u'Nejprve si svůj e-mail zaregistrujte', 'warning')
                redirect(url_for('login_create_account'))
            raw_email = email
            email = base64.b64encode(email)
            token = md5("%s|%s" % (app.secret_key, email)).hexdigest()
            url = url_for(
                'login_click_from_email_password',
                token=token,
                email=email,
                _external=True)

            if app.debug:
                flash(url, "debug")

            send_mail(
                u'Obnovení hesla',
                raw_email,
                "data/reset-password.md",
                url)
            return redirect(url_for('login_forgotten_verify'))
    else:
        form = EmailForm(request.args)

    return render_template('login_forgotten.html', form=form, menu=menu())


@app.route("/login/resetovat-heslo/overeni-emailu/")
def login_forgotten_verify():
    return render_template('login_forgotten_verify.html')


@app.route("/login/resetovat-heslo/odkaz/", methods=['GET', 'POST'])
def login_click_from_email_password():
    email = request.args.get('email', None)
    token = request.args.get('token', None)

    if token == md5("%s|%s" % (app.secret_key, email)).hexdigest():
        email = base64.b64decode(email)
        session['reset-email'] = email
        flash(u'Váš e-mail byl ověrěn, nyní nastavte nové heslo', 'success')
        return redirect(url_for('login_reset_password'))
    flash(
        u'Platnost odkazu již vypršela, nebo je odkaz v nespárvném tvaru',
        'warning')
    return redirect(url_for('login_forgotten_password'))


@app.route('/login/resetovat-heslo/', methods=['POST', 'GET'])
def login_reset_password():
    email = session.get('reset-email', None)
    if not email:
        abort(403)

    if request.method == "POST":
        form = PasswordForm(request.form)
        if form.validate():
            user_hash = resolve_user_by_email(email)
            update_password(user_hash, email, form.data.get('password', None))
            next = session.get('next', None)
            session.clear()
            session['user_hash'] = user_hash
            flash(u'Heslo bylo změneno', 'success')
            return redirect(next or url_for('index'))
    else:
        form = PasswordForm()
    return render_template('login_reset_password.html', form=form, menu=menu())


### MAIL ###
def send_mail(subject, to, message_file, url=""):
    mail = Mail(app)
    body = read_file(message_file) or ""
    body = body % {
        'url': url,
        'ip': request.remote_addr,
        'user_agent': request.user_agent,
        'mail': to,
    }

    msg = Message(
        subject,
        recipients=[to],
        sender=(u"Petr Joachim", "petr@joachim.cz")
    )
    msg.body = body
    msg.html = markdown.markdown(body)
    mail.send(msg)


def read_file(filename):
    return open(filename).read().decode('utf-8')


### FORMS ###
class LoginForm(Form):
    email = TextField('E-mail', validators=[Required(), Email()])
    password = TextField('Heslo', validators=[Required()])


class PasswordForm(Form):
    password = TextField('Heslo', validators=[Required(), EqualTo(
        'confirm', message=u'Hesla se musí shodovat')])
    confirm = TextField(u'Potvrzení', validators=[])


class EmailForm(Form):
    email = TextField('E-mail', validators=[Required(), Email()])


class BasicForm(Form):
    fullname = TextField(u'Jméno', validators=[Required()])
    password = TextField('Heslo', validators=[Required()])


class SettingsForm(Form):
    name = TextField(u'Jméno a příjmení', validators=[Required()])
    bio = TextField('Bio')
    company = TextField('Firma')
    web = TextField('Web')
    twitter = TextField('Twitter')
