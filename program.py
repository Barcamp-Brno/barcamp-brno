# coding: utf-8
from barcamp import app
from flask import render_template, Markup, url_for
from login_misc import check_auth
from utils import menu
from talks import get_talks_dict
from datetime import time, date, datetime

den_d = date(2015, 5, 23)


{

}

times = [
        {'block_from': time(8, 30), 'block_to': time(9, 0), 'date': den_d, 'data': u'Otevření vstupu a registrace'},
        {'block_from': time(9, 0), 'block_to': time(9, 30), 'date': den_d, 'data': u'Oficiální zahájení - D105'},
        {'block_from': time(9, 45), 'block_to': time(10, 30), 'date': den_d, 'data': {
            'd105': 'cf5c5d27', # 604x Petr Ludwig / Jak zlepšit svoje myšlení? 
            'd0206': 'f3a76e01', # !!! musi byt rano 313x Robert Němec / Proč reklamní kampaně nefungují 
            'd0207': 'e72aa5e7', # 225x Michal 'may' Hrubý / K úspěchu skrze přátele a lidi kolem nás 
            'e104': '929531d7', # 163x Přemysl Krajčovič / Temná strana SCRUMu 
            'e105': 'bcc82a1c', # 156x Evel Meckarov / Super Vzdělávání - 7 tajemství efektivního rozvoje a vzdělávání 
            'e112': '28941568', # 72x Roman Kümmel / Vyhackuj si motorku aneb internetové soutěže pod kontrolou hackerů 
            'a112': {'rows': 2, 'anchor': 'cipov', 'user': u'Peter Cipov', 'title': u'Coding Dojo'},
            'a113': {'rows': 2, 'anchor': 'poboril', 'user': u'Jan Pobořil', 'title': u'Drupal kickstart pro úplné začátečníky'},
        }},
        {'block_from': time(10, 45), 'block_to': time(11, 30), 'date': den_d, 'data': {
            'd105': 'f791244d', # 493x Petr Jezevec Pouchlý /  ! Nežerte motivační bullshit 
            'd0206': '7cf2346d', # 324x !!! musi byt dopoledne Jan Řezáč / Krysí závody ♦ aneb webdesignerem snadno a rychle 
            'd0207': 'ded0b30f', # 224x Jan Pospíšil / Jak se dělá Booking.com 
            'e104': '0730ebea', # 171x Adam Motvička / Chci podnikat, ale nevím v čem ani jak! 
            'e105': '5ae653b1', # 153x Ondřej Materna / Pár právních rad pro startupisty 
            'e112': 'af161fe1', # 35x Ondřej Krátký / Liftago: 5 překážek úspěchu ve start-upu   
            'a112': {},
            'a113': {},
        }},
        {'block_from': time(11, 45), 'block_to': time(12, 30), 'date': den_d, 'data': {
            'd105': '9d9ad7c5', # 403x David Grudl / Můj první sex 
            'd0206': '396d8174', # 236x Tereza Venerová / Návod na použití UX designera / For Dummies 
            'd0207': 'a7848677', # 210x Michal Toman / Najděte FLOW ve své práci! 
            'e104': 'ef5df8f9', # 173x Milan Tříska / Úspěšné inzertní strategie na Facebooku 
            'e105': '41037bba', # 144x Barbora Nevosadova / Jak se dostat do novin 
            'e112': '4279dcd8', # 13x !!! musi byt dopoledne Marek Vacek / Seznam.cz: AB testy, izomorfní aplikace, docker a machine learning 
            'a112': {'rows': 2, 'anchor': 'brumbalova', 'user': u'Albina Brumbálová & Richard Gracla', 'title': u'Komunikační improvizace'},
            'a113': {'rows': 2, 'anchor': 'kohout', 'user': u'František Kohout', 'title': u'Symfony2'},
        }},
        {'block_from': time(12, 30), 'block_to': time(13, 45), 'date': den_d, 'data': u'Oběd'},
        {'block_from': time(13, 45), 'block_to': time(14, 30), 'date': den_d, 'data': {
            'd105': '3aadfecd', # 397x Martin Zákostelský / Oslovil jsem 208 holek během dvou měsíců: Jak to dopadlo a co jsem se díky tomu dozvěděl o ženách i o sobě 
            'd0206': '31547b2d', # 254x Filip Dřímalka / To nejlepší z digitálních inovací - startupy, aplikace, online služby, technologie. Speciální narozeninová přednáška :) 
            'd0207': '758228ab', # 208x Dušan Vystrčil / Návod na přežití v informační době: Jak se nepřesytit? 
            'e104': 'f67dd771', # 177x Daniel Gamrot / Evernote prakticky pro každodenní použití 
            'e105': 'ed7c7b25', # 130x Jana Leitnerová / 1 metoda, jak hasit komunikační průšvihy na sociálních sítích 
            'e112': 'de9ce362', # 27x Hynek Heřmanský / Co říká vaše ucho vašemu mozku? 
            'a112': {'rows': 1, 'anchor': 'kummel', 'user': u'Roman Kümmel', 'title': u'Vyhackujte si webovou soutěž'},
            'a113': {'rows': 2, 'anchor': 'henniova', 'user': u'Jasmína Henniová', 'title': u'Prezentační dovednosti v praxi'},
        }},
        {'block_from': time(14, 45), 'block_to': time(15, 30), 'date': den_d, 'data': {
            'd105': '910ce464', # 399x Michal Ondra / Umění ušetřit čas a delegovat 
            'd0206': 'b3022215', # 257x Michal Hanych / V jaké formě začít podnikat? OSVČ nebo s.r.o.? 
            'd0207': 'cd31f05c', # 196x Pavel Šíma / SEO, které zachraňuje životy 
            'e104': 'ad97130f', # 178x BoBMarvan / Redesign webu za 5 dní 
            'e105': 'c6563967', # !!! musi byt odpoledne 147x Tereza Jechová / MOJE STARÁ UŽ MĚ NEBAVÍ aneb jak si najít tu pravou... práci! 
            'e112': 'dbdd7c64', # 27x Jan Bareš / Jazykový Guláš – aneb jak správně uvařit zdroje pro překladatele 
            'a112': {'rows': 1, 'anchor': 'siller', 'user': u'Petr Šiller', 'title': u'Uživatelské testování v praxi'},
            'a113': {},
        }},
        {'block_from': time(15, 45), 'block_to': time(16, 30), 'date': den_d, 'data': {
            'd105': 'd616d02c', # 386x Kristýna FitCoach Baštářová / Sedíte často, sedíte hodně?  Jak si nevysedět bolesti zad a zdravotní komplikace. 
            'd0206': '7e1d6ac1', # 320x Kamil Gregor / Jak kriticky myslet? Praktický návod 
            'd0207': '9e775a20', # 193x Pavel Lasak / Nechte za sebe pracovat Excel  
            'e104': '0ee2dc57', # 183x Jaroslav Kováč / Mistrovství v prezentacích #2: Jak konečně zapůsobit na emoce publika? 
            'e105': '1a5ab764', # 128x Berka BerkaUX / Jak se stát UX profesionálem aneb vzdělávání jinak 
            'e112': '30fe233f', # 14x Vanda Cabanová / Czechitas - jak a proč děláme, co děláme 
            'a112': {'rows': 2, 'anchor': 'klimesova', 'user': u'Veronika Klimešová & Radek Dobrovolný', 'title': u'Pro-Action Café: Jak vyřešit problém a nepohádat se u toho'},
            'a113': {'rows': 1, 'anchor': 'bobek', 'user': u'Martin Bobek & Petr Flégl', 'title': u'Agile versus Waterfall fight'},
        }},
        {'block_from': time(16, 45), 'block_to': time(17, 30), 'date': den_d, 'data': {
            'd105': '4473a121', # 358x Martin Lutonský / 90% životopisů končí v koši. Aneb jak zajistit, aby mezi nimi nebyl i ten Váš! 
            'd0206': '2d8aa867', # 352x Pavel Čech / Jak přednášet, aby vám ostatní naslouchali 
            'd0207': '12e8241f', # 186x Lukáš Nevosád / Agilní řízení firmy 
            'e104': 'b9b7d53a', # 180x Michal Mervart / Jak sestavit skvělý brief a pomoci tím klientovi i sobě 
            'e105': 'd936dd8e', # 126x Adam Herout / Jak (ne)prznit statistiku 
            'e112': '4779786a', # 7x Vladimír Coufal / Jak se vyvíjí 3D tiskárna 
            'a112': {},
            'a113': {'rows': 1, 'anchor': 'krajcovic', 'user': u'Přemysl Krajčovič', 'title': u'Agile testing prostřednictvím reality'},
        }},
        {'block_from': time(17, 30), 'block_to': time(18, 0), 'date': den_d, 'data': u'Zakončení akce'},
        {'block_from': time(19, 0), 'block_to': time(23, 0), 'date': den_d,
            'data': Markup(u'<a href="/' + app.config['YEAR'] + u'/stranka/afterparty.html">Afterpárty</a>')},
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
    t.insert(1, 
        {'block_from': time(20, 0), 'block_to': time(23, 59), 'date': date(2015, 2, 22),
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
