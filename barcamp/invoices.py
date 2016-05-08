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
from collections import defaultdict

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
    user_invoices = app.redis.smembers(KEYS['user_invoices'] % user['user_hash'])
    invoices = []
    if user_invoices:
        invoices = sorted(
            filter(
                lambda x: bool(x),
                map(
                    lambda invoice: json.loads(invoice or 'false'),
                    app.redis.mget(
                        user_invoices
                    )
                )
            ),
            key=lambda x: x['number'],
            reverse=True
        )
    return render_template('moje-objednavky.html', user=user, invoices=invoices, sizes=SIZES)


@app.route('/objednavky/prehled')
@auth_required
@is_admin
def invoices_admin():
    all_invoices = app.redis.smembers(KEYS['year_invoices'])
    invoices = []
    invoices = sorted(
        filter(
            lambda x: bool(x),
            map(
                lambda invoice: json.loads(invoice or 'false'),
                app.redis.mget(
                    all_invoices
                )
            )
        ),
        key=lambda x: x['number'],
        reverse=True
    )
    pending_price = reduce(
        lambda x, y: x + y['total_price'],
        filter(
            lambda x: x['status'] == 'new',
            invoices
        ),
        0
    )
    collected_price = reduce(
        lambda x, y: x + y['total_price'],
        filter(
            lambda x: x['status'] == 'paid',
            invoices
        ),
        0
    )
    collected_sizes = defaultdict(lambda: 0)
    pending_sizes = defaultdict(lambda: 0)
    for invoice in invoices:
        if invoice['status'] == 'new':
            target = pending_sizes
        elif invoice['status'] == 'paid':
            target = collected_sizes
        else: continue

        for size in SIZES:
            target[size] += invoice[size]

    form = InvoicePaidForm()

    return render_template(
        'prehled-objednavek.html',
        invoices=invoices,
        sizes=SIZES,
        form=form,
        pending_price=pending_price,
        pending_sizes=pending_sizes,
        collected_price=collected_price,
        collected_sizes=collected_sizes,
    )


@app.route('/objednavky/zaplatit/', methods=['POST'])
@auth_required
@is_admin
def invoice_update_status():
    if request.method == "POST":
        form = InvoicePaidForm(request.form)
        if form.validate():
            invoice_number = form.data.get('order_number')
            invoice = json.loads(app.redis.get(KEYS['invoice'] % invoice_number))
            old_status = invoice['status']
            if old_status != 'paid':
                #send mail
                mail(
                    u'Objednávka zaplacena',
                    'petr@joachim.cz',
                    invoice['email'],
                    'data/paid-order.md',
                    invoice,
                    sender_name=u'Petr Joachim / Barcamp Brno'
                )

            invoice['status'] = 'new'
            app.redis.set(KEYS['invoice'] % invoice_number, json.dumps(invoice))
            flash(u'Objednávka číslo {number} za {total_price} kč zaplacena'.format(**invoice), 'success')
            return redirect(url_for('invoices_admin'))
    flash()
    return redirect(url_for('invoices_admin'))


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

class InvoicePaidForm(Form):
    order_number = IntegerField(u'Objednávka', validators=[DataRequired(u'Tohle musíš zadat')])
