# coding: utf-8
from barcamp import app
from flask import render_template, Markup
from talks import get_talks_dict
from workshops import get_workshops_dict
from datetime import time, date, datetime
den_d = date(2018, 6, 2)


times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupů a registrací (otevřeno je po celý den)'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - Kino Scala'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'scala': (
                'c83ba428', # business 45 145x Martin Lutonský / Vyjednávej bez okolků aneb zajisti si (rychle a účinně), to co chceš - praktické tipy a triky co a kdy říct 
                    ),
            'baroko': (
                'db1223c4', # marketing 45 69x Lukáš Dadej / VELKÝ BRATR tě sleduje >>> škaredá pravda o Facebooku 
                    ),
            'it': (
                '590915b2', # development 45 106x Tomáš Brukner / Jak se vzdělávat v IT, aby vám neujel technologický vlak? 
                    ),
            'partners': (
                '41a7d057', # partner/inovations 45 21x Artur Kane / How Insider Threats Challenge Digital Economy, Real Life Attacks explained! 
                    ),
            'workshop1':
                'f94c6a76', # 115minut Matěj Krejčí DigiDetox - Jak získat kontrolu
            'workshop2':
                'bd2f43d7', # 120minut Pavel Szabo Na volné noze vzdáleně a nezávisle odkudkoliv na světě
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'scala': (
                '79630a79', # inovations 45 140x Hanka Březinová _ Inspirata.cz / Motivace zaměstnance v 21. století - 10 ověřených pravd 
                    ),
            'baroko': (
                '34f8af6c', # marketing 45 73x Filip Novák / Youtube marketing 
                    ),
            'it': (
                '42ecf6ed', # development 45 76x Dominik Tilp / Na frameworku (ani jazyku) nezáleží 
                    ),
            'partners': (
                'b9603559', # partner/development 45 21x Přemysl Krajčovič / Jak jsme začali házet naše appky do kontejneru 
                    ),
            'workshop1': '',
            'workshop2': '',
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'scala': (
                '58284f8f', # business 45 143x Richard Kunovský / Jak si vytvořit doživotní rentu? 
                    ),
            'baroko': (
                '0c009760', # inovations 45 85x Jan Meravy / 10 zaujímavých technológií budúcnosti 
                    ),
            'it': (
                'a44bc297', # development 45 66x Martin Podborský / Výhody práce v Týmu aneb Proč někdy nemám rád své kolegy 
                    ),
            'partners': (
                '69530f9b', # partner/inovations 45 39x Tomáš Koudar / Be AGILE, not frAGILE: Jak doručovat agilně a nezbláznit se z toho 
                    ),
            'workshop1':
                'd6fb05b1', # 60minut Veronika Dostálová GDPR v emailingu
            'workshop2':
                '34310e5b', # 55minut Lea Kolkopova Svobodné kreslení
        }},
        {'block_from': time(12, 30), 'block_to': time(13, 45), 'date': den_d, 'data':
            #Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/catering.html">Oběd</a>')
            u'Oběd'
        },
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'scala': (
                '642a354f', # inspirational 45 123x Minutový Petr Krejčí / 5 nejčastějších chyb při prezentování „Minutový řečník“ aneb jak se zbavit trémy z mluvení na veřejnosti 
                    ),
            'baroko': (
                'a9b3f57f', # marketing 45 93x Veronika Dostálová / Zbavte se základních chyb v emailingu 
                    ),
            'it': (
                '85cd04c1', # development 45 63x Jan Hadrava / Scrum Master: 10 důvodů, proč tě nenávidím 
                    ),
            'partners': (
                '614c955b', # partner/development 45 14x Martin Dulák / Jak si vydělat první milion na Atlassian Marketplace 
                    ),
            'workshop1':
                '97426abc', # 115minut Barbara Palatová Daně v kostce Workshop by se měl konat v místnosti s projektorem a tabulí nebo flipchartem.
            'workshop2':
                '6373d483', # 115minut Honza Řehák Mindfulness v každodenních situacích vol.2
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'scala': (
                '6b3c1cd1', # business 45 129x Jaroslav Kováč / Realita brněnských realit v2018
                    ),
            'baroko': (
                '90e53d70', # inspirational 45 88x Mirka Papajiková / Denní rituály - jak, proč a co vlastně 
                    ),
            'it': (
                '2ddb19bf', # development 45 61x Matouš Kutypa / Tajemství čistého a dobře napsaného kódu 
                    ),
            'partners': (
                '6203620f', # partner/development 45 25x David Fogl / Testování mobilních aplikací (jde to i levně) 
                    ),
            'workshop1': '',
            'workshop2': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'scala': (
                'a12c36f6', # design 45 133x Jan Řezáč / Web jako továrna na zákazníka 
                    ),
            'baroko': (
                '0302ef5c', # design 45 92x Marek Čevelíček / Tohle dej na web! 
                    ),
            'it': (
                '82697f62', # development 45 55x Michal Vyšinský / Sdílení UI komponent napříč aplikacemi 
                    ),
            'partners': (
                '20506e68', # development 45 15x Lukas Kocourek - Život Integračního architekta v korporátu bez ESB s králíkem v clusteru
                    ),
            'workshop1':
                '8c8e6d25', # 90minut Darja Jochimová Jak tvořit poutavý obsah na sociální sítě v roce 2018?
            'workshop2': '',
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'scala': (  
                'e70035db', # inspirational 45 110x Vít Skalický / Jak vyprávět příběhy
                    ),
            'baroko': (
                'e6e18489', # inovations 45 86x Veronika Dohnalová / Zavádění prvků Hapiness Managementu ve velké nadnárodní firmě - co se lidem líbilo a co byl propadák? 
                    ),
            'it': (
                '0df5100f', # development 45 51x Jiří Materna / Milníky, výzvy a limity současné umělé inteligence 
                    ),
            'partners': (
                    ),
            'workshop1': '',
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