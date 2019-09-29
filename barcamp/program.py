# coding: utf-8
from .barcamp import app
from flask import render_template, Markup
from .talks import get_talks_dict
from .workshops import get_workshops_dict
from datetime import time, date, datetime
den_d = date(2019, 10, 5)

"""
"""


times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupů a registrací (otevřeno je po celý den)'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - Kino Scala'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': 'a438a88c', # [approved] 90min 30x - Radek Šimčík / Jak na stres? Meditace, dýchací cvičení, hudba v praxi,
            'workshop2': '38bea4bd', # [approved] 90min 30x - Lucie Mairychová, Veronika Lokajová, Maria Anna Bednariková / Raketovou rychlostí kupředu - manuál pro úspěšný vstup studenta na trh práce,
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': '',
            'workshop2': '',
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': '615f8ea9', # [approved] 30min 30x - Hana Klimentová / Návrh vizitky za 30 minut
            'workshop2': 'ca0c61f3', # [approved] 60min 30x - Hanka Březinová / Jak vybrat ten správný teambuilding nebo trénink, který vašim lidem sedne!,
        }},
        {'block_from': time(12, 30), 'block_to': time(13, 45), 'date': den_d, 'data':
            #Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/catering.html">Oběd</a>')
            u'Oběd'
        },
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': '82d25b71', # [approved] 60min 30x - Vladimír Macháček / Jak udělat e-shop z jakékoliv webové stránky do 30 minut,
            'workshop2': 'cfed55d0', # [approved] 90min 24x - Mirka Papajiková / Hravě a zdravě v těle,
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': 'b41bd72c', # [approved] 60min 15x - M.arter, Jana Pokorná, Markéta Mrkvová, Andrea Bohačíková / Byznys během rodičovské,
            'workshop2': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': 'placeholder',
            'workshop2': '5b6c7c56', # [approved] 90min 30x - Matej Chyľa / Návrh prezentačného webu, na ktorý budete hrdý,
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'scala': (
                    ),
            'baroko': (
                    ),
            'it': (
                    ),
            'partners': (
                    ),
            'workshop1': 'placeholder',
            'workshop2': '',
        }},
        {'block_from': time(17, 30), 'block_to': time(18, 0), 'date': den_d, 'data': u'Zakončení akce'},
        {'block_from': time(19, 0), 'block_to': time(23, 59), 'date': den_d,
            'data': Markup(u'Afterpárty')},#u'<a href="/' + app.config['YEAR'] + u'/stranka/after-social-event.html">Afterpárty</a>')},
        {'block_from': time(23, 45), 'block_to': time(23, 59), 'date': den_d,
            'data': Markup(u'Poslední objednávky')},
    ]
@app.route('/%s/aktualne.html' % app.config['YEAR'])
def program_aktualne():
    t = times[::]
    t.insert(0,
        {'block_from': time(18, 0), 'block_to': time(23, 59), 'date': date(2016, 6, 3),
            'data': Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/warm-up-social-event.html">Warm-up párty</a>')}
    )
    actual_date = datetime.now().date()
    actual_time = datetime.now().time()
    next_times = []
    for event in t:
        if (event['date'] == actual_date and event['block_to'] >= actual_time)\
                or event['date'] > actual_date:
            next_times.append(event)
    return render_template(
        'aktualne.html',
        talks=get_talks_dict(),
        times=next_times,
        workshops=get_workshops_dict(),
    )
