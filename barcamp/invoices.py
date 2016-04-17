# coding: utf-8

import json
from datetime import datetime
from barcamp import app
from flask import render_template, url_for, redirect, request, flash
from login_misc import check_auth, auth_required, is_admin
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from utils import mail
from entrant import user_user_go

INVOICE_NUMBER_START = 102016000;
SIZES = ['man_s', 'man_m', 'man_l', 'man_xl', 'man_xxl', 'woman_xs', 'woman_s', 'woman_m', 'woman_l', 'woman_xl']
UNIT_PRICE = 150

KEYS = {
    'invoice_number': 'invoice_number_%s' % app.config['YEAR'],
    'invoice': 'invoice_%s_%%s' % app.config['YEAR'],
    'user_invoices': 'user_invoices_%s',
    'year_invoices': 'year_invoices_%s' % app.config['YEAR'],
}


@app.route('/chci-si-objednat/', methods=['GET', 'POST'])
@auth_required
def invoices():
    user = check_auth()
    if request.method == "POST":
        form = InvoiceForm(request.form)
        if form.validate():
            invoice = form.data
            invoice['total_price'] = sum([UNIT_PRICE * invoice.get(size, 0) for size in SIZES])
            invoice = insert_invoice(invoice, user)
            flash(u'Objednávka číslo {number} za {total_price} kč zaznamenána'.format(**invoice), 'success')
            user_user_go(user)
            return redirect(url_for('my_invoices'))
    else:
        default = dict((size, 0) for size in SIZES)
        default['name'] = user['name']
        default['email'] = user['email']
        form = InvoiceForm(** default)
    return render_template('objednavka.html',
        user=user, form=form, shirt_price=UNIT_PRICE)


@app.route('/objednavky/moje')
def my_invoices():
    user = check_auth()
    invoices = sorted(
        filter(
            lambda x: bool(x),
            map(
                lambda invoice: json.loads(invoice or 'false'),
                app.redis.mget(
                    app.redis.smembers(KEYS['user_invoices'] % user['user_hash'])
                )
            )
        ),
        key=lambda x: x['number'],
        reverse=True
    )
    return render_template('moje-objednavky.html', user=user, invoices=invoices)


@app.route('/objednavky/prehled')
@auth_required
@is_admin
def invoices_admin():
    invoices = sorted(
        filter(
            lambda x: bool(x),
            map(
                lambda invoice: json.loads(invoice or 'false'),
                app.redis.mget(
                    app.redis.get(KEYS['year_invoices'])
                )
            )
        ),
        key=lambda x: x['number'],
        reverse=True
    )
    return render_template('prehled-objednavek.html', invoices=invoices)


@app.route('/objednavky/zmenit/<new_state>/<order_number>')
@auth_required
@is_admin
def invoice_update_status(new_state, order_number):
    pass


def insert_invoice(invoice, user):
    app.redis.setnx(KEYS['invoice_number'], INVOICE_NUMBER_START)
    invoice_number = app.redis.incr(KEYS['invoice_number'])
    invoice['number'] = invoice_number
    invoice['user'] = user
    invoice['ip'] = request.remote_addr
    invoice['date'] = datetime.now().isoformat()
    invoice['user_agent'] = str(request.user_agent)
    invoice['status'] = 'new'

    app.redis.set(KEYS['invoice'] % invoice_number, json.dumps(invoice))
    app.redis.sadd(KEYS['user_invoices'] % user['user_hash'], KEYS['invoice'] % invoice_number)
    app.redis.sadd(KEYS['year_invoices'], KEYS['invoice'] % invoice_number)
    # send inovice mail
    mail(
        u'Objednávka k potvrzení',
        'petr@joachim.cz',
        user['email'],
        'data/new-order.md',
        invoice,
        sender_name=u'Petr Joachim / Barcamp Brno'
    )
    return invoice

def at_least_one_piece(form, field):
        have_some_pieces = any(
            map(
                lambda size: int(getattr(form, size).data) > 0,
                SIZES
            )
        )
        if not have_some_pieces:
            raise  ValidationError(u'Musíš vybrat alespoň jeden kus')

class InvoiceForm(Form):
    name = TextField(u'Celé jméno', validators=[DataRequired(u'Tohle musíš zadat')])
    email = TextField(u'E-mail', validators=[DataRequired(u'Tohle musíš zadat'), Email(u'A tohle je email?')])
    phone = TextField(u'Telefon', validators=[DataRequired(u'Tohle musíš zadat')])
    street = TextField(u'Ulice', validators=[DataRequired(u'Tohle musíš zadat')])
    city_zip = IntegerField(u'PSČ', validators=[DataRequired(u'Tohle musíš zadat')])
    city = TextField(u'Město', validators=[DataRequired(u'Tohle musíš zadat')])
    # company = TextField('Firma')
    # company_number = TextField(u'IČO')
    other = TextField(
        u'Poznámka k objednávce',
        widget=TextAreaField()
    )

    sizes = TextField('', validators=[at_least_one_piece])

    man_s = IntegerField(u'S')
    man_m = IntegerField(u'M')
    man_l = IntegerField(u'L')
    man_xl = IntegerField(u'XL')
    man_xxl = IntegerField(u'XXL')

    woman_xs = IntegerField(u'XS')
    woman_s = IntegerField(u'S')
    woman_m = IntegerField(u'M')
    woman_l = IntegerField(u'L')
    woman_xl = IntegerField(u'XL')
