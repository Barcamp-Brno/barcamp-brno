# coding: utf-8
from barcamp import app
from flask import render_template
from login_misc import check_auth
from utils import menu


times = [
        {'block_from': '8:30', 'block_to': '9:00', 'data': u'Začátek a registace'},
        {'block_from': '9:00', 'block_to': '9:30', 'data': u'Zahájení'},
        {'block_from': '9:45', 'block_to': '10:00', 'data': {
            'd105':
                '191ff524', # Petr Ludwig / Osobní efektivita - výběr 10 nejúčinnějších tipů
            'd0206':
                '9e22733b', # Jan Kovalčík / Slevová žumpa
            'd0207':
                '75139daa', # Robert Janák / Sazba versus Typografie
            'e105':
                '01d489a6', # Luděk Kvapil / Art of Trolling
            'e112':
                '5350e135', # Filip Dřímalka / Podnikání v 21. století - special edition
        }},
        {'block_from': '10:45', 'block_to': '11:30', 'data': {
            'd105':
                '8cc9eb88', # Adam Herout / Co je špatného na vysoké škole
            'd0206':
                'd103d31e', # Miroslav Holec / Co mě život naučil o vývoji (nejen webových) aplikací
            'd0207':
                'c2a4391a', # Jana Leitnerová / Born to be PR!
            'e105':
                '01a3aedf', # Michal Hantl / Jak přestat chodit do práce a začít vydělávat pro programátory
            'e112':
                'ff648560', # Jaroslav Homolka / 100 DAYS OF RIDING - MAD NOT BAD - sólo moto expedice na východ a zpět - co jsem se naučil
        }},
        {'block_from': '11:45', 'block_to': '12:30', 'data': {
            'd105':
                '9ca09674', # Tereza Venerová / 10 minut denně
            'd0206':
                '6cf3d18a', # David Hořínek / Fenomén finančního poradenství - jak funguje?
            'd0207':
                '9b1df0e0', # Martin Lutonský / Mozek - tvůj parťák nebo nepřítel?
            'e105':
                'afc4c4c6', # Ondřej Materna / Jak se kradou nápady
            'e112': None,
        }},
        {'block_from': '12:45', 'block_to': '13:30', 'data': u'Oběd'},
        {'block_from': '13:45', 'block_to': '14:30', 'data': {
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
        {'block_from': '14:45', 'block_to': '15:30', 'data': {
            'd105':
                'caa28ab6', # Barbora Nevosadova / Jak propagovat mobilní aplikaci
            'd0206':
                '22430230', # Roman Hřebecký / Dělej si to klidně sám!
            'd0207':
                '24376166', # Petr Jezevec Pouchlý / To nejlepší z židovských anekdot o práci s lidmi
            'e105':
                '741bbc0f', # Ivan Kutil | @codeas / Matematika s nastraženýma ušima
            'e112':
                'e4d17deb', # Martin Jarčík / Buďte agilní, ne debilní
        }},
        {'block_from': '15:45', 'block_to': '16:30', 'data': {
            'd105':
                '88b75dc5', # Petr Zemek / Od hamburgeru ke krávě aneb jak z binárky získat zdroják
            'd0206':
                'f831c73a', # BerkaUX / Jak začít dělat skutečné UX
            'd0207':
                '49f1a810', # Peter Krutý / Čtení výrazů lidské tváře
            'e105':
                '0962c89a', # Charlie Greenberg / 6 otázek úspěchu
            'e112':
                '2ea99053', # ysoft / Mlč a pádluj, Amerika je daleko...
        }}, 
        {'block_from': '16:45', 'block_to': '17:30', 'data': {
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
        }},
        {'block_from': '17:30', 'block_to': '18:00','data': u'Zakončení akce'},
    ]


@app.route('/program/')
def program():
    return render_template(
        'program.html',
        menu=menu(),
        times=times,
        user=check_auth()
    )


@app.route('/aktualne/')
def program_aktualne():
    return render_template(
        'aktualne.html',
        menu=menu(),
        user=check_auth()
    )
