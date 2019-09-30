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
                '13d67ff8', # [business-marketing] 117x - Jaroslav Kováč / Realita brněnských realit v3
                    ),
            'baroko': (
                '64ccb043', # [business-marketing] 89x - Lukáš Lesovský / Automatizace v online marketingu. Hrozba nebo pomocník?
                    ),
            'it': (
                'placeholder', # flowmon partnerska prednaska - zatim nedodali
                    ),
            'partners': (
                '92cd49b1', # [inspirational] 54x - Filip Holec, Marian Hurta / Efektivní vzdělávání (nejen) v IT aneb co jsme se naučili za 3 roky praxe s našimi studenty
                    ),
            'workshop1': 'a438a88c', # [approved] 90min 30x - Radek Šimčík / Jak na stres? Meditace, dýchací cvičení, hudba v praxi,
            'workshop2': '38bea4bd', # [approved] 90min 30x - Lucie Mairychová, Veronika Lokajová, Maria Anna Bednariková / Raketovou rychlostí kupředu - manuál pro úspěšný vstup studenta na trh práce,
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'scala': (
                '1a586200', # [business-marketing] 99x - Filip Novák / Jak najít a obhájit správnou cenu za své služby
                    ),
            'baroko': (
                '3ddf5a22', # [inspirational] 86x - Vít Skalický / Jak prezentovat zajímavě i nezajímavá témata
                    ),
            'it': (
                '8dea4dd5', # [development] 81x - Lukáš Antal / Sociální inženýrství, aneb nejsnazší metoda hackingu
                    ),
            'partners': (
                '70890a38', # [business-marketing] 76x - Jan Ševčík / O kolik peněz přicházíte, když nevyužíváte všechny funkce webového prohlížeče.
                    ),
            'workshop1': '',
            'workshop2': '',
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'scala': (
                '45bb8e55', # [inspirational] 165x - Tomáš Rygl / Jdi si za svým, dokud je čas
                    ),
            'baroko': (
                '93015acb', # [inspirational] 59x - Karel Dytrych / Život bez doktora: challenge accepted 💪
                    ),
            'it': (
                'c85808e8', # [development] 77x - Marek Čevelíček / Zlepšujeme web – Použitelnost a přesvědčivost na webu
                    ),
            'partners': (
                '6a59257a', # Zdenek Hyrak - narhadni misto za workshop - pretahne se do obeda
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
                '459dc9a0', # [business-marketing] 128x - Hanka Březinová (inspirata.cz) / Prezentuj (se) jako hvězda aneb umění prodat své myšlenky.
                    ),
            'baroko': (
                '00743784', # [business-marketing] 90x - Michal Orsava a Michaela Lovecká / Za oponou virálních videí s mnoha miliony zhlédnutí! (Harry Potter v česku s Milošem Zemanem a další)
                    ),
            'it': (
                'afd67f00', # [development] 47x - Jakub Čížek / Hospodyňka v8: Chytrá domácnost s prvky A.I., která vám rozsvítí, pokud nebude v depresi
                    ),
            'partners': (
                '6b20dbbb', # [inspirational] 55x - Nela Ďopanová / Příběh udržitelného pohybu
                    ),
            'workshop1': '82d25b71', # [approved] 60min 30x - Vladimír Macháček / Jak udělat e-shop z jakékoliv webové stránky do 30 minut,
            'workshop2': 'cfed55d0', # [approved] 90min 24x - Mirka Papajiková / Hravě a zdravě v těle,
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'scala': (
                '78f0efd8', # [inspirational] 151x - Richard Kunovský / Jak se stát spokojeným rentiérem
                    ),
            'baroko': (
                'e49d98c6', # [business-marketing] 79x - Ondřej Pešák / Jak vytvořit reklamní strategii, aby klient nezkrachoval
                    ),
            'it': (
                'd45e76ff', # [development] 48x - Zdeněk Soukup / Nejnudnější práce na světě?
                    ),
            'partners': (
                '5f630c96', # [inspirational] 51x - Roman Čelechovský / Jak nepsat jako češtinářská lama
                    ),
            'workshop1': 'b41bd72c', # [approved] 60min 15x - M.arter, Jana Pokorná, Markéta Mrkvová, Andrea Bohačíková / Byznys během rodičovské,
            'workshop2': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'scala': (
                'ef7b9527', # [business-marketing] 137x - Pavel Cahlík / Odhalte, jak s vámi značky manipulují
                    ),
            'baroko': (
                '6a319e3a', # [inspirational] 61x - Mirka Papajiková / Jak na tělo, aby vydrželo
                    ),
            'it': (
                '614cc3e8', # [development] 48x - Jan Ševčík / Nativní aplikace jsou mrtvé! Google věří PWA
                    ),
            'partners': (
                'ef2028d6', # [design] 67x - Marek Malík / Design sprint: Jak v 5 dnech vyřešit složité problémy a otestovat nové nápady
                    ),
            'workshop1': 'placeholder',
            'workshop2': '5b6c7c56', # [approved] 90min 30x - Matej Chyľa / Návrh prezentačného webu, na ktorý budete hrdý,
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'scala': (
                '6d084eab', # [inspirational] 74x - Honza Mayer / Největší průser v mém životě: Jak jsem nabral do firmy hvězdu ze zahraničí #cultureclash
                    ),
            'baroko': (
                '210ac008', # [business-marketing] 94x - Andrea Grigerová / Můžu výběrem písma ovlivnit to, jak se lidé rozhodnou?
                    ),
            'it': (
                '7b493f80', # [development] 66x - Martin Haller / Pojďme společně hacknout server
                    ),
            'partners': (
                '57be0f4f', # [business-marketing] 70x - Vít Schaffarczik / Jak jsme zvýšili počet objednávek z Facebooku o 500 %
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
