# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash, render_template
from login_misc import check_auth, auth_required
from login import send_mail
from talks import get_talks_dict
from entrant import user_user_go
from collections import defaultdict
from entrant import get_entrants
from datetime import time, date, datetime

KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
}

@app.route("/jedna-dve-tri-ctyri-pet/")
@auth_required
def prepocet_hlasu():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    data = defaultdict(lambda: 0)
    keys = app.redis.keys('votes_%s_*' % app.config['YEAR'])
    for key in keys:
        members = app.redis.smembers(key)
        for member in members:
            data[member] += 1

    talk_tuples = app.redis.zrevrange(KEYS['talks'], 0, -1, withscores=True)
    for talk, score in talk_tuples:
        if 0 is not int(score - data.get(talk, 0)):
            print "update talk %s from %d to %d votes" % (talk, score, data.get(talk, 0))
            app.redis.zadd(KEYS['talks'], talk, data.get(talk, 0))

    return "omg"


@app.route('/jede-jede-postacek/')
@auth_required
def plneni_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    entrants = get_entrants()
    for entrant in entrants:
        app.redis.sadd('newsletter', entrant['email'])

    return 'omg'


@app.route('/posli-osly/')
def poslani_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    for mail in app.redis.smembers('newsletter'):
        print mail
        app.redis.srem('newsletter', mail)
        continue

        send_mail(
            u'Barcamp Brno 2013, ohlédnutí za akcí',
            '', #mail,
            'data/newsletter.md')

    return 'omg2'


@app.route('/funguj-prosim/')
def test_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    send_mail(
        u'Barcamp Brno 2013, ohlédnutí za akcí',
        'tomas@sotoniak.cz',
        'data/newsletter.md')

    return 'uff'

times = [
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '191ff524', # Petr Ludwig / Osobní efektivita - výběr 10 nejúčinnějších tipů
            'd0206':
                '9e22733b', # Jan Kovalčík / Slevová žumpa
            'd0207':
                '75139daa', # Robert Janák / Sazba versus Typografie
            'e105':
                '01d489a6', # Luděk Kvapil / Art of Trolling
            'e112':
                '2ea99053', # ysoft / Mlč a pádluj, Amerika je daleko...
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '8cc9eb88', # Adam Herout / Co je špatného na vysoké škole
            'd0206':
                'f831c73a', # BerkaUX / Jak začít dělat skutečné UX
            'd0207':
                'c2a4391a', # Jana Leitnerová / Born to be PR!
            'e105':
                '01a3aedf', # Michal Hantl / Jak přestat chodit do práce a začít vydělávat pro programátory
            'e112':
                'ff648560', # Jaroslav Homolka / 10 DAYS OF RIDING - MAD NOT BAD - sólo moto expedice na východ a zpět - co jsem se naučil
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '9ca09674', # Tereza Venerová / 10 minut denně
            'd0206':
                '6cf3d18a', # David Hořínek / Fenomén finančního poradenství - jak funguje?
            'd0207':
                '9b1df0e0', # Martin Lutonský / Mozek - tvůj parťák nebo nepřítel?
            'e105':
                'afc4c4c6', # Ondřej Materna / Jak se kradou nápady
        }},
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '9bc8cc97', # František Churý / Lean Startup Machine aneb jak validovat podnikatelský nápad během 48 hodin (ukázky na příkladech)
            'd0206':
                'e0eb2c28', # Vladimír Kuchař / Medonosný marketing aneb jak získat více zákazníků a přitom neutrácet více peněz za reklamu
            'd0207':
                '4a50162d', # Pavel Šíma / Bullshity o malých eshopech
            'e105':
                '6372e8c8', # Evel Meckarov / Moc - Za každým šampionem stojí tým - plavba davem a objevení Ameriky - být nejlepší a tvrdě pracovat k úspěchu nestačí
            'e112':
                '8a2772f1', # Adam Hazdra / Techno je zpátky! aneb to byste tady nečekali
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                'caa28ab6', # Barbora Nevosadova / Jak propagovat mobilní aplikaci
            'd0206':
                '22430230', # Roman Hřebecký / Dělej si to klidně sám!
            'd0207':
                '24376166', # Petr Jezevec Pouchlý / To nejlepší z židovských anekdot o práci s lidmi
            'e105':
                'nahrada',  # '741bbc0f', # Ivan Kutil | @codeas / Matematika s nastraženýma ušima
            'e112':
                'e4d17deb', # Martin Jarčík / Buďte agilní, ne debilní
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '88b75dc5', # Petr Zemek / Od hamburgeru ke krávě aneb jak z binárky získat zdroják
            'd0206':
                'd103d31e', # Miroslav Holec / Co mě život naučil o vývoji (nejen webových) aplikací
            'd0207':
                '49f1a810', # Peter Krutý / Čtení výrazů lidské tváře
            'e105':
                '0962c89a', # Charlie Greenberg / 6 otázek úspěchu
            'e112':
                '5350e135', # Filip Dřímalka / Podnikání v 21. století - special edition
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': date(2013, 6, 15), 'data': {
            'd105':
                '666220de', # Igor Szoke / Geekovo minimum umělé inteligence
            'd0206':
                '1f45f0e8', # Michal Janík / Povídání o SEO, PPC, vyhledávačích zboží, PR, display reklamě, firemních katalozích, e-mailingu, sociálních médiích či remarketingu
            'd0207':
                '506f7afa', # Štěpán Bechynský / Internet of Things
            'e105':
                '86472f44', # Richard Kafoněk / Myslete strategicky, aneb perfektní exekutiva nestačí
            'e112':
                '5fc9015a', # Boris Šuška & Zbyněk Nedoma / Yet another Silicon Valley story
        }}
    ]

@app.route('/program-rc/')
def rc_program():
    return render_template(
        'rc-talks.html',
        times=times,
        page_style='program',
        talks=get_talks_dict(),
    )

