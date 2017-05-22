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
            'd105': (
                    '78bbd19a', # business 45 158x Martin Lutonský / Komunikační triky v praxi aneb poznej do minuty na jaké komunikační vlně jezdí tvůj partner
                    ),
            'e112': (
                    '6369c617', # development 45 65x Dominik Tilp / Frontend Performance (když React a Webpack nejsou řešení)
                    ),
            'd0206': (
                    '18f4b86c', # design 22 54x Michal Mervart / UX pro e-shopy
                    'f9484fdd', # design 22 6x Martin Králík / S Červenou královnou až do Uměleckoprůmyslového muzea
                    ),
            'd0207': (
                    '7f04c7a7', # inspirational 45 87x Matěj Krejčí / F*ck It, F*ck them, F*ck them all - vol.2
                    ),
            'e104': (
                    'b029734d', # inovations 45 49x Dominik Novozámský / Mindrák - jak pochopit a ovlivnit chování týmu, zákazníka a celého světa
                    ),
            'e105': (
                    'c94564b4', # marketing 45 33x Milan Tříska / Brandování na výkon: Třetí noha Facebooku
                    ),
            'a112': 'f7e8177f', #Aleš Vrána (115 minut) - Jak se naučit koučovat
            'a113': 'f1faaae0', #Honza Řehák (115 minut) - Mindfulness v každodenních situacích
            'c228': 'bf59d5df', #Petr Augustin (115 minut) - Rapid prototyping pro UX designéry i nedesignéry
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'd105': (
                    '20f2e876', # marketing 45 123x Marek Hnátek / Jak na účinný marketing webu, když nemáme velký rozpočet?
                    ),
            'e112': (
                    '4b30589d', # inspirational 22 80x Hanka Březinová / Nežerte sendviče!! ... aneb jak někomu sdělit, že je "debil" a neurazit ho
                    '9018ea0b', # inspirational 22 74x Karel Fuksa / Co takhle vzít svou kariéru do vlastních rukou?
                    ),
            'd0206': (
                    'fe798c31', # business 45 99x Jaroslav Kováč / Realita brněnských realit :-X
                    ),
            'd0207': (
                    'cce0b224', # development 22 38x Pavel Šindelář / To nejpodstatnější ze světa (nejen) platebních karet
                    '855c9184', # development 22 37x Michał Weiser / Web front-end workflows
                    ),
            'e104': (
                    '9d7fc7b3', # xxx 45 7x HeliScan z FIT do Austrálie a zpět (aneb jak jsem na opačném konci světa přebíral novou technologii)
                    ),
            'e105': (
                    '7c7e0a23', # inovations 22 29x Lukáš Nevosád / 360° videa: Jak natočit svět a přinést ho uživatelům do obýváku pomocí VR
                    'fb972b52', # inovations 22 28x Dominik Pinter / Jak měníme hotelový průmysl bez jediného vlastního serveru.
                    ),
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'd105': (
                    'fbd65388', # inspirational 22 122x Matouš Kutypa / Dostaň více peněz za svou práci
                    '9bfab62e', # inspirational 22 105x Radek Zahradník / Hackujeme Tinder! Aneb sex snadno, rychle a zadarmo!
                    ),
            'e112': (
                    '928bc4a5', # marketing 22 82x Pavel Ungr / Zeptej se na co chceš v SEO! #TrueBarcamp
                    '95f1cf54', # marketing 22 74x Jan Kužel / Jak za pár dnů z nuly najít a oslovit emailem stovky potenciálních klientů a neposrat se z toho
                    ),
            'd0206': (
                    '0ee9a8ff', # development 22 44x Matouš Kutypa / Jak zajistit bezpečnost Vaší webové aplikace
                    '840326a8', # development 22 40x Marek Salát / React, Redux ES6 starter pack
                    ),
            'd0207': (
                    '6e2b4a88', # business 45 96x Petr Janošík / Jak z Brna rozjet globální startup se 100 000 uživateli za 10 měsíců a dostat investici 10M?
                    ),
            'e104': {
                    'category': 'inovations', # inovations L
                    },
            'e105': ('',), # DESIGN volny slot
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
            'd105': (
                    'd252a3d9', # inovations 45 90x Lucie Radová / Digitální nomádství na třech kontinentech, s manželem a v tuktuku
                    ),
            'e112': (
                    '6ad55d76', # inspirational 45 54x Aleš Vrána / Jak vypadá koučování živě?
                    ),
            'd0206': {
                    'category': 'development', # development L
                    },
            'd0207': {
                    'category': 'design', # design L
                    },
            'e104': (
                    '1821ae19', # marketing 22 36x Zuzana Hiklová / Marketing naslepo
                    'b4da1b15', # marketing 22 37x Jan Bleha / Práce s IT komunitami pro zlepšení náboru
                    ),
            'e105': (
                    'e85ab109', # business 22 69x Hanka Březinová / 5 x 5 koučovacích otázek pro ulehčení vašeho rozhodování
                    '25e62e83', # business 22 65x Matouš Kutypa / Kolik peněz potřebuješ na rozjezd firmy? Aneb bez peněz do byznysu nelez
                    ),
            'a112': 'a79edb11', #Barbora Nevosadova (115 minut) - Jak napsat tiskovku, která neskončí v koši
            'a113': '7c4a0548', #Robert Janák (115 minut) - InDesign – sazba učebnic, prac. postupy pro tvorbu EPUB, šablony
            'c228': '',
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'd105': (
                    '0ff37e92', # business 22 156x Jezevec | Court of Moravia / Nenech ze sebou vydrbávat! Kolik doopravdy stojí hodina práce freelancera?
                    '4157d7e1', # business 22 96x Marek Čevelíček / Faily při tvorbě e-shopů, za které zaplatíte víc, než za celý e-shop. Jak je nedělat?
                    ),
            'e112': (
                    '68221b85', # design 22 76x Jan Petr / Search UX best practices: Relevance, rychlost, použitelnost
                    '3654c4ba', # design 22 74x Jan Kužel / Jak se sám naučit vytvářet animované vysvětlovací videa (a k čemu je to vůbec dobré)
                    ),
            'd0206': (
                    'd65f9a89', # inovations 45 61x Radek Zahradník / Na volné noze a digitální nomádství v praxi. S hypotékou na krku
                    ),
            'd0207': (
                    '7c7f6c74', # marketing 45 58x Daniel Nytra / 17 našlapaných tipů pro emailový marketing a automatizaci prodeje
                    ),
            'e104': (
                    'b4266fd2', # inspirational 45 52x Edita Dostálová / Tajemství úspěchu: myslete jako ti úspěšní a bohatí
                    ),
            'e105': (
                    '6236c839', # development 22 35x Michał Weiser / CSS at scale
                    '9d61666a', # development 22 33x Kamil Řezníček / DevOps a jak jsme s ním začínali
                    ),
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'd105': (
                    '44b14da4', # design 22 138x Michal Drapák / Za všechno může dizajn, aneb psychologie v reklamě
                    '1fba4a51', # design 22 88x Hana Klimentová / Grafika pro negrafiky aneb Když grafik nemá čas
                    ),
            'e112': (
                    '0b790a2b', # inovations 22 80x Honza Vaňhara / Home 2.0 aneb Inteligentní bydlení
                    '41ac43d2', # inovations 22 74x Ondřej Zukal / Chci se zautomatizovat
                    ),
            'd0206': {
                    'category': 'business', # inovace L
                    },
            'd0207': {
                    'category': 'marketing', # marketing L
                    },
            'e104': (
                    '3c658889', # development 45 36x Martin Péchal / Jak škálovat webovou aplikaci, aby zvládla 100 000 uživatelů online?
                    ),
            'e105': {
                    'category': 'inspirational', # inspirational L
                    },
            'a112': '4c102eb1', #martin krcek (115 minut) - Vytvoř si svého ChatBOTa. Bez programování. Za pár minut.
            'a113': '535f0ba3', #Jan Petr (115 minut) - Nechte uživatele vyhledávat ve vašem obsahu rychlostí myšlenky
            'c228': '',
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'd105': (
                    '6ce39478', # development 22 98x Jakub Čížek / Jak jsem si za pár dolarů postavil chytrou domácnost, chrochtající váhu a robotické autíčko Bobík
                    'fc04a087', # development 22 63x Michal Pietrik / Jak psát udržovatelné UI testy
                    ),
            'e112': (
                    '9118afb1', # marketing 22 89x Michal Filípek / 11x hacků a F*ckupů ve Facebook reklamě za 11 Millionů !!!!
                    '05277b8c', # marketing 22 26x Lukáš Dadej / *** 10x hacků a F*ckupů ve Facebook reklamě za 10 Millionů Kč! ***
                    ),
            'd0206': (
                    '3296142e', # design 45 30x Honza Slavík / Jak bych řešil EET, kdybych byl ministr financí
                    ),
            'd0207': (
                    'e9cf09fa', # inovations 45 52x Senta Čermáková / Až naši práci převezmou roboti ...
                    ),
            'e104': (
                    'ccbbc98e', # business 22 81x Lubomír Černý / Objevte sílu odlišnosti a uspějte v marketingu!
                    '7f4bb46b', # business 22 71x Karol Jarkovsky / Ako presrať 12 mil. a dostať za to povýšené
                    ),
            'e105': (
                    '185772c6', # inspirational 45 48x Berka BerkaUX / Odstraňme tabu, bavme se o smrti
                    ),
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