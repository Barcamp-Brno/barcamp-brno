# coding: utf-8

import base64
from datetime import datetime
from hashlib import md5

from flask import render_template, session, redirect, flash
from flask import url_for, request, abort

from flask_wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

from .login_misc import auth_required, resolve_user_by_email, login_redirect, authorized_redirect
from .login_misc import check_auth, create_account, gdpr_consent_required
from .login_misc import update_password, create_update_profile, store_gdpr_consent

from .mailing import send_message_from_template
from .barcamp import app

KEYS = {
    'account': 'account_%s',
    'email': 'email_%s',
    'twitter': 'twitter_%s',
    'gdpr': 'gdpr_consent_%s' % app.config['YEAR'],
    'gdpr_date': 'gdpr_consent_date_%s' % app.config['YEAR'],
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

    if check_auth(skip_gdpr_check=True):
        flash(u'Nyní jste přihlášen', 'success')
        session['next'] = None
        return authorized_redirect(next or url_for('login_settings'))

    return render_template("login.html", form=form)


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
    return render_template('nastaveni.html', user=user, form=form)


@app.route("/logout/")
def logout():
    session.clear()
    flash(u'Nyní jste odhlášen', 'success')
    return redirect(url_for('index'))


@app.route('/login/registrace/zalozeni-uctu/', methods=['GET', 'POST'])
def login_create_account():
    if request.method == "POST":
        form = ConsentEmailForm(request.form)
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
            email_b64 = base64.b64encode(email.encode()).decode()

            token = md5(f"{app.secret_key}|{email_b64}".encode()).hexdigest()
            url = url_for(
                'login_click_from_email',
                token=token,
                email=email_b64,
                _external=True)

            if app.debug:
                flash(url, "dark")

            send_message_from_template(
                email,
                u'Vytvoření účtu',
                "data/verify-account.md",
                {'url': url})
            return redirect(url_for('login_email_verify'))
    else:
        form = ConsentEmailForm()
    return render_template('login_create_account.html', form=form)


@app.route("/login/registrace/overeni-emailu/")
def login_email_verify():
    return render_template('login_email_verify.html')

@app.route("/login/registrace/odkaz-z-mailu/")
def login_click_from_email():
    email = request.args.get('email', None)
    token = request.args.get('token', None)

    if token == md5(f"{app.secret_key}|{email}".encode()).hexdigest():
        email = base64.b64decode(email).decode()
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
            store_gdpr_consent({'email': email, 'user_hash': user_hash})
            session.clear()
            session['user_hash'] = user_hash
            flash(u'Nyní jste přihlášen', 'success')
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
            if not resolve_user_by_email(email):
                flash(u'Nejprve si svůj e-mail zaregistrujte', 'warning')
                redirect(url_for('login_create_account'))
            email_b64 = base64.b64encode(email.encode()).decode()
            token = md5(f"{app.secret_key}|{email_b64}".encode()).hexdigest()
            url = url_for(
                'login_click_from_email_password',
                token=token,
                email=email_b64,
                _external=True)

            if app.debug:
                flash(url, "dark")

            send_message_from_template(
                email,
                u'Obnovení hesla',
                "data/reset-password.md",
                {"url": url})
            return redirect(url_for('login_forgotten_verify'))
    else:
        form = EmailForm(request.args)

    return render_template('login_forgotten.html', form=form)


@app.route("/login/resetovat-heslo/overeni-emailu/")
def login_forgotten_verify():
    return render_template('login_forgotten_verify.html')


@app.route("/login/resetovat-heslo/odkaz/", methods=['GET', 'POST'])
def login_click_from_email_password():
    email = request.args.get('email', None)
    token = request.args.get('token', None)

    if token == md5(f"{app.secret_key}|{email}".encode()).hexdigest():
        email = base64.b64decode(email).decode()
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
            session.clear()
            session['user_hash'] = user_hash
            flash(u'Heslo bylo změneno', 'success')
            return redirect(url_for('index'))
    else:
        form = PasswordForm()
    return render_template('login_reset_password.html', form=form)


@app.route('/login/gdpr/', methods=['POST', 'GET'])
def gdpr_consent():
    user = check_auth(skip_gdpr_check=True)
    if not user:
        return login_redirect()

    if request.method == "POST":
        form = ConsentForm(request.form)
        if form.validate():
            store_gdpr_consent(user)
            return redirect(url_for('index'))
    else:
        form = ConsentForm()
    return render_template('login_gdpr_consent.html', user=user, form=form)


### FORMS ###
class LoginForm(Form):
    email = TextField('E-mail', validators=[DataRequired(), Email()])
    password = TextField('Heslo', validators=[DataRequired()])


class PasswordForm(Form):
    password = TextField('Heslo', validators=[DataRequired(), EqualTo(
        'confirm', message=u'Hesla se musí shodovat')])
    confirm = TextField(u'Potvrzení', validators=[])


class EmailForm(Form):
    email = TextField('E-mail', validators=[DataRequired(), Email()])


class ConsentEmailForm(Form):
    email = TextField('E-mail', validators=[DataRequired(), Email()])
    gdpr_consent = BooleanField(
        u'Souhlas',
        validators=[DataRequired()],
        default=False)


class ConsentForm(Form):
    gdpr_consent = BooleanField(
        u'Souhlasím se zpracováním údajů',
        validators=[DataRequired()],
        default=False)
    mailchimp_consent = BooleanField(
        u'Souhlasím s přihlášením do newsletteru',
        default=True
    )


class BasicForm(Form):
    fullname = TextField(u'Jméno', validators=[DataRequired()])
    password = TextField('Heslo', validators=[DataRequired()])


class SettingsForm(Form):
    name = TextField(u'Jméno a příjmení', validators=[DataRequired()])
    bio = TextField('Bio')
    company = TextField('Firma')
    web = TextField('Web')
    twitter = TextField('Twitter')
