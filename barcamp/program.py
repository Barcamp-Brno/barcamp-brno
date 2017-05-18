# coding: utf-8
from barcamp import app
from flask import render_template, Markup
from talks import get_talks_dict
from workshops import get_workshops_dict
from datetime import time, date, datetime

den_d = date(2017, 6, 3)


times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupu a registrací (otevřeno je po celý den)'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - D105'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': 'f7e8177f', #Aleš Vrána (115 minut) - Jak se naučit koučovat
            'a113': 'f1faaae0', #Honza Řehák (115 minut) - Mindfulness v každodenních situacích
            'c228': 'bf59d5df', #Petr Augustin (115 minut) - Rapid prototyping pro UX designéry i nedesignéry
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': '5f9310e5', #Matej Minárik (55 minut) - Forms in Angular
            'a113': 'd137feaf', #Michal Štorkán (55 minut) - ZBOŽÁKOVÁ REVOLUCE aneb na velikosti (e-shopu) nezáleží
            'c228': '54272f4d', #BaraKahoun (30 minut) - Too much information?
        }},
        {'block_from': time(12, 30), 'block_to': time(13, 00), 'date': den_d, 'data':
            Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/catering.html">Oběd</a>')
        },
        {'block_from': time(13, 00), 'block_to': time(13, 45), 'date': den_d, 'data':
            Markup(u'')
        },
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': 'a79edb11', #Barbora Nevosadova (115 minut) - Jak napsat tiskovku, která neskončí v koši
            'a113': '7c4a0548', #Robert Janák (115 minut) - InDesign – sazba učebnic, prac. postupy pro tvorbu EPUB, šablony
            'c228': '',
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': '4c102eb1', #martin krcek (115 minut) - Vytvoř si svého ChatBOTa. Bez programování. Za pár minut.
            'a113': '535f0ba3', #Jan Petr (115 minut) - Nechte uživatele vyhledávat ve vašem obsahu rychlostí myšlenky
            'c228': '',
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'd105': '',
            'e112': '',
            'd0206': '',
            'd0207': '',
            'e104': '',
            'e105': '',
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(17, 30), 'block_to': time(18, 0), 'date': den_d, 'data': u'Zakončení akce'},
        {'block_from': time(19, 0), 'block_to': time(23, 59), 'date': den_d,
            'data': Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/after-social-event.html">Afterpárty</a>')},
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
