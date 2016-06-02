# coding: utf-8
from barcamp import app
from flask import render_template, Markup
from talks import get_talks_dict
from workshops import get_workshops_dict
from datetime import time, date, datetime

den_d = date(2016, 6, 4)            

times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupu a registrací (otevřeno je po celý den)'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - D105'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'd105': 'ee2cd560', # 0 227x "Minutový" Petr Krejčí / Jak si vybudovat osobní značku na Facebooku a LinkedInu? 
            'e112': '3fb68188', # 13 136x Víťa Janeček / Proč váš produkt selže aneb 5 pravidel pro úspěšné podnikání 
            'd0206': 'bea84558', # 14 133x Barbora Nevosádová & Lukáš Nevosád / Jak si vydělat na Teslu vývojem mobilních aplikací 
            'd0207': '58d4cdca', # 21 112x Swenia Toupalik / Nechte Photoshop pracovat pro vás a nenechte se jím ovládnout... aneb Photoshop tipy, které vás zachrání před šílenstvím. 
            'e104': '292723a7', # 30 91x Radek Zahradník / Práce na volné noze aneb zpověď freelancčíka od srdíčka 
            'e105': '1587a681', # 41 74x Lukáš Dadej / *** Facebook Marketing for Heroes *** 
            'a112': '5a276c78', # Vladimír Přichystal / Workshop - Hodinová optimalizace inzerce na Heurece
            'a113': '93b0cd5a', # Karel KAIX Rujzl / Workshop — Základy OpenRefine (nejen) pro PPCčkaře
            'c228': '845cf26b', # Rosta Urbánek / Workshop — Zbožáky a jak z nich vymačkat maximum
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'd105': 'f3ebffbe', # 1 218x Kristýna FitCoach Baštářová / Sedavé zaměstnání - hoaxy a pravdy o dlouhodobém sezení. 
            'e112': 'e5aedaf5', # 12 139x Vojtěch Kounovský / Jak si říci o zvýšení platu -  Co dělat pro svůj vysněný plat a jak funguje kompenzace, co nadřízeného potěší a co už méně. 
            'd0206': '88490216', # 18 118x Dominik Tilp / JavaScript kouzel zbavený 
            'd0207': 'e69e8f6e', # 23 111x Jirka Chomát / Špičkový produkt nepotřebuje marketing
            'e104': '4a7c0e50', # 29 93x Tomáš Švec / Babysitting miliardy liber 
            'e105': 'a938d504', # 40 75x Petr Hýna / Škálování agilního vývoje 
            'a112': '73a24fe0', # Aleš Vrána / Workshop — Jak se stát koučem?
            'a113': '',
            'c228': '7418afaa', # Juraj Komloši / Workshop — Bezpečnosť webových aplikácii - ako odhaliť SQL injection, XSS a ďalšie zraniteľnosti?
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'd105': '39a76dc8', # 2 216x Martin Kuchař / IT Soft skills v 21. století 
            'e112': '13c8cc19', # 11 142x Marian Hurta  Filip Holec / Jak začít s IT a najít práci do 3 měsíců? 
            'd0206': 'ae1f401e', # 20 112x Lubo Smid / STRV Silicon Valley Story 
            'd0207': 'c015334c', # 25 104x Roman Dušek / Co se reálně vyhledává na Seznam.cz? 
            'e104': 'e77603fa', # 34 80x Petr Bláha / A/B testováním proti hrochovi 
            'e105': '941166e3', # 37 76x Corinth / Proč udává v Silicon Valley trendy pro ne-herní VR a AR zrovna startup z Brna? 
            'a112': '',
            'a113': '91f920f6', # Radek Zahradník / Workshop — Windows deployment v licenčně omezeném prostředí aneb vaříme widle pouze a jenom s pomocí W10
            'c228': '',
        }},
        {'block_from': time(12, 30), 'block_to': time(13, 00), 'date': den_d, 'data':
            Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/catering.html">Oběd</a>')
        },
        {'block_from': time(13, 00), 'block_to': time(13, 45), 'date': den_d, 'data':
            Markup(u'Koncert Solitutticelli Cello Ensemble')
        },
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'd105': '4fdd20c7', # 3 215x Honza Řehák / Ovládni pozornost, nakopni motivaci! 
            'e112': '07fe9d4b', # 9 154x František Churý / Podnikání prakticky aneb jak ověřit podnikatelský nápad během 48 hodin (ukázky na příkladech) 
            'd0206': '5094a664', # 17 125x Tonda Moravec / 10 způsobů jak zaručeně dovrtat firemní kulturu 
            'd0207': 'e84e68b1', # 24 105x Petr Urbánek / KODÉR. — bez pičovin! 
            'e104': '95145ab7', # 31 86x Jana Meinlschmidtova / Mluv dřív, než otevřeš pusu. 
            'e105': '49922495', # 39 76x Lukáš Vrábel / Animovaný úvod do základov (hlbokých konvolučných) neurónových sietí a deep learningu. 
            'a112': '7e026fde', # David Bureš / Workshop — ESP8266: Internet věcí a Azure
            'a113': '01f159fe', # Jirka Chomát / Workshop — Prezentace produktů na webu
            'c228': '7641bec1', # Dominik Tilp / Workshop — React + Redux server side rendering
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'd105': 'c42e63a8', # 4 202x Pavel Čech / UX Design aneb jak tvořit pro lidi 
            'e112': '5c3610a6', # 10 144x Evel Meckarov / Kariera Budoucnosti. 6 Trendu ktere ovlivni vasi karieru do 6ti let 
            'd0206': '5af5faba', # 15 133x Martin Lutonský / CV-hack aneb jak zaválet na přijímacím pohovoru a ne tam jen tak hekat... 
            'd0207': 'f76d29d1', # 22 111x Michal Talanda / Co by se měl každý manažer naučit od dětí v mateřské školce. 
            'e104': '70915aec', # nahrada Petr Svoboda
            'e105': '93480356', # 38 76x Jan Markel / Prodej svoje know-how online 
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'd105': '104422b4', # 5 172x Daniel Danny Dubravec / Když si založíte eshop a za měsíc si pro vás přijde policie 
            'e112': '5fc37b64', # 8 159x Mirka Papajiková /  Jak stav těla ovlivňuje kvalitu života 
            'd0206': '99b14a70', # 19 117x Janek Rubes / Jak dostat taxikáře do polepšovny - Praha vs. Prachy 
            'd0207': 'be2d7b58', # nahrada Michal Ergens
            'e104': 'f89ae7e6', # 33 80x Veronika Dohnalová & Barbora Pečeňová / 5 klíčů k organizaci úspěšné konference 
            'e105': '278c27e6', # 36 78x Berka BerkaUX / 20 let zaměstnancem aneb mýty volnonožců 
            'a112': '101ffdb9', # Peter Cipov / Workshop — TDD coding dojo
            'a113': 'ee536e59', # Swenia Toupalik / Workshop — Produktové fotografie prakticky aneb jak na hezké produktovky
            'c228': 'c63fb8f7', # Matěj Nosál / Workshop — RTB přes Adform
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
           'd105': 'c79e143e', # 6 171x Matěj Krejčí / F*ck It, F*ck them, F*ck them all
            'e112': '4ec235aa', # 7 170x Martin Halík / Jak designujeme Skypicker #UX #design 
            'd0206': '609b12f6', # 16 126x Jezevec | Court of Moravia / Byznys vám valí, ale lidi v týmu... 
            'd0207': 'b49da296', # 27 96x Marek Hnátek / Linkbuilding včera a dnes – jak získat kvalitní odkazy pro libovolný web 
            'e104': 'ef7342b7', # nahrada Jan Kalianko
            'e105': '8a0b1c0f', # 35 79x Honza Slavík / Strasti a pasti projektového řízení 
            'a112': '',
            'a113': '',
            'c228': '',
        }},
        {'block_from': time(17, 30), 'block_to': time(18, 0), 'date': den_d, 'data': u'Zakončení akce'},
        {'block_from': time(19, 0), 'block_to': time(20, 0), 'date': den_d,
            'data': Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/after-social-event.html">Afterpárty</a>')},
        {'block_from': time(20, 0), 'block_to': time(21, 0), 'date': den_d,
            'data': Markup(u'Začátek diskuzí se speakry souběžně se zahájením networkingového eventu Impact HUB Brno')},
        {'block_from': time(21, 0), 'block_to': time(21, 30), 'date': den_d,
            'data': Markup(u'Charitativní dražba třech unikátních kusů triček Barcamp Brno 2016 na podporu Josepha')},
        {'block_from': time(21, 30), 'block_to': time(22, 30), 'date': den_d,
            'data': Markup(u'Vsuvka v podobě živého hudebního překvapení od LMC')},
        {'block_from': time(23, 45), 'block_to': time(23, 59), 'date': den_d,
            'data': Markup(u'Poslední objednávky')},
    ]


@app.route('/%s/aktualne.html' % app.config['YEAR'])
def program_aktualne():
    t = times[::]
    t.insert(0,
        {'block_from': time(19, 0), 'block_to': time(23, 59), 'date': date(2016, 6, 3),
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
