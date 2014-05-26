# coding: utf-8
from barcamp import app
from flask import render_template, Markup, url_for
from login_misc import check_auth
from utils import menu
from talks import get_talks_dict
from datetime import time, date, datetime

den_d = date(2014, 5, 31)

times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupu a registrace'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - D105'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'e112': '8f420b99', # XXX dopoledne / 95x Lukáš Maňásek / Obchodování v 50 °C 
            'd105': 'bb4031aa', # 383x Peter Krutý / Psychologie v Prezentovani 
            'd0206': '227b8f4b', # 216x Swenia Toupalik / Photoshop finty, které vám ulehčí život 
            'd0207': 'a9207afa', # 170x Karel Koupil / Inteligentní e-mailový marketing 
            'e105': 'e053f529', # 105x Peter Širka / ♛ node.js v praxi + tvoríme v ňom moderné aplikácie (WebSocket, Angular.js, atď.) 
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'e112': 'ee34d277', # XXX dopoledne nebo po obede / 134x Marcel Fejtek / 100 zemí, 100 zákonů a ještě více norem… aneb jak prodat chytrou krabičku do celého světa 
            'd105': '469849be', # 391x Petr Ludwig / Jak najít osobní vizi, nejsilnější motivátor našeho života 
            'd0206': '10338554', # 183x Martin Lutonský / Myšlení, náš chléb - základy denní osobní efeftivity 
            'd0207': '2c9679ba', # XXX prvni nebo druhy cas / 149x Jan Řezáč / Jak vypsat výběrové řízení na web
            'e105': 'bf617a48', # 107x Richard Fridrich / Selfies - experiment, ktorý som nenávidel 
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'e112': 'd4505563', # XXX 10:30 - 15:30 / 6x Kateřina Andrlová / Jak se pomáhá dětem v Africe 
            'd105': '383123cb', # 322x Adam Herout / Tři principy veřejného mluvení 
            'd0206': '4967fc68', # 179x Jiří Vicherek / Sex, cigarety a štěňátka - základy pick-up a networkingu 
            'd0207': '713cde0b', # 167x Daniel Gamrot / Evernote aneb Neztrácejte čas hledáním informací 
            'e105': '4df11c67', # 109x Vladimír Šandera / Jak využívat live chat jako marketingový nástroj - nový způsob komunikace na webu 
        }},
        {'block_from': time(12, 45), 'block_to': time(13, 10), 'date': den_d, 'data': u'Oběd'},
        {'block_from': time(13, 10), 'block_to': time(13, 30), 'date': den_d, 'data': 
            Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/doprovodny-program.html#kentico">Polštářová bitva</a>')},
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'e112': None,
            'd105': '5f9818b6', # 293x Filip Dřímalka / Absolut Lifehacks // How to Hack Your Work and Life 
            'd0206': '949089ea', # 183x Jan Tomáš / Návratnost User Experience 
            'd0207': '0a83d27a', # 154x Honza Slavík / Jak na projekty a nezbláznit se 
            'e105': '9c658519', # 111x Michal Lupečka / Neprogramuj, pokud to není nezbytně nutné 
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'e112': 'cf0012e7', # 85x Stanislav Hacker / Javascript. Dobrý sluha, špatný pán 
            'd105': 'c4853366', # 257x Berka BerkaUX / Svoboda v práci prakticky 
            'd0206': 'd058b3b7', # 183x Jan "Kali" Kalianko / Já dělám to SEO dobře, jen vyhledávače ho zatím nepochopily... 
            'd0207': '687362c6', # 147x Petr Bechyně / Jak neuspět se svým webem na internetu 
            'e105': 'd68de999', # 111x Lukáš Nevosád / Android vs. iOS aneb Platform Wars! 
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'e112': '2203f3fe', # 36x Jaroslav Homolka / Fair Play je investice 
            'd105': '1a9fa56d', # 241x Evel Meckarov / SuperProjekťák - 7 tajemství projektového řízení - řešte všechno přes projekt a uspějete!  
            'd0206': 'd58978e8', # 189x Marek Mencl / ---Jak si najít smysluplnou práci?--- 
            'd0207': '99373761', # 140x Petr Halík / PPC dnes - jak vypadat mají, jak ne a proč umí rychle odpovídat na byznysové otázky 
            'e105': 'ba1c1e72', # 124x Petr Jezevec Pouchlý / ☞ Zpověď korporátčíka od srdíčka ☜ 
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'e112': 'b48aa7cb', # XXX po obede / 31x Janek Rubes / Jak se tvoří na Stream.cz 
            'd105': 'e78df29f', # 233x Michal Hantl / Google Analytics pro startupy 
            'd0206': 'fc52c755', # 178x Robert Němec / 10 věcí, které jsem se naučil při tvorbě nového webu RobertNemec.com 
            'd0207': 'fd876707', # XXX po 15:45 / 156x Stanislav Gálik / The Best of Psychologie přesvědčování COMPILATION sex tape 
            'e105': 'ed5f993f', # 113x Matej Kvasňovský / Agilný redesign rozsiahlej webovej aplikácie Kentico 
        }},
        {'block_from': time(17, 30), 'block_to': time(18, 0), 'date': den_d, 'data': u'Zakončení akce'},
        {'block_from': time(19, 0), 'block_to': time(23, 0), 'date': den_d,
            'data': Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/afterparty.html">Kentico Afterpárty</a>')},
    ]


@app.route('/%s/program.html' % app.config['YEAR'])
def program():
    return render_template(
        'program.html',
        menu=menu(),
        times=times,
        talks=get_talks_dict(),
        user=check_auth()
    )


@app.route('/%s/aktualne.html' % app.config['YEAR'])
def program_aktualne():
    t = times[::]
    t.insert(0, 
            {'block_from': time(18, 0), 'block_to': time(19, 0), 'date': date(2013, 6, 14),
            'data': Markup(u'<a href="/stranka/warmup/">Honza Řezáč</a>')}
    )
    t.insert(1, 
        {'block_from': time(20, 0), 'block_to': time(23, 59), 'date': date(2013, 6, 14),
            'data': Markup(u'<a href="/stranka/warmup/">Warm-up párty</a>')}
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
        menu=menu(),
        talks=get_talks_dict(),
        times=next_times,
        user=check_auth()
    )
