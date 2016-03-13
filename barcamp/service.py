# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash, render_template, Response
from login_misc import check_auth, auth_required
from login import send_mail
from talks import get_talks_dict, get_talks
from entrant import user_user_go
from collections import defaultdict
from entrant import get_entrants
from datetime import time, date, datetime
from program import times
import io
import csv

KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
}

@app.route('/service/vyvoleni')
@auth_required
def service_vyvoleni():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    # talks, extra_talks = get_talks()
    talk_hashed = get_talks_dict()
    talks = []
    for t in times:
        if type(t['data']) is dict:
            for room in ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105'):
                talk = talk_hashed.get(t['data'][room], None)
                if talk:
                    talks.append(talk)

    # talks = talks[:35]
    output = io.BytesIO()
    writer = csv.writer(output, delimiter=";", dialect="excel", quotechar='"')

    writer.writerow([
        'video',
        'name',
        'email',
        'web',
        'company',
        'twitter',
        'title',
        'detail_url'
        'description',
        'purpose',
        'other'
    ])

    for talk in talks:
        user = talk['user']
        _ = [
            talk['video'],
            user['name'],
            user['email'],
            talk['web'],
            talk['company'],
            talk['twitter'],
            talk['title'], 
            'http://www.barcampbrno.cz%s' % url_for('talk_detail', talk_hash=talk['talk_hash']),
            talk['description'].replace("\r\n", "<br/>"),
            talk['purpose'].replace("\r\n", "<br/>"),
            talk['other'].replace("\r\n", "<br/>")
        ]
        writer.writerow([unicode(s).encode("utf-8") for s in _])

    return Response(output.getvalue(), mimetype="text/plain")


@app.route('/service/do-programu')
@auth_required
def service_do_programu():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    talks, extra_talks = get_talks()
    talks = talks[:35]
    output = io.BytesIO()

    for talk in extra_talks:
        user = talk['user']
        #output.write(("'e112': '%s', # %sx %s / %s \r\n" % (talk['talk_hash'], talk['score'], user['name'], talk['title'])).encode('utf-8'))
        output.write(("e112: <%s>\r\n" % (user['email'])).encode('utf-8'))
    
    rooms =  'd105', 'd0206', 'd0207', 'e104', 'e105'
    for i, talk in enumerate(talks):
        user = talk['user']
        #output.write(("'%s': '%s', # %sx %s / %s \r\n" % (rooms[i//7], talk['talk_hash'], talk['score'], user['name'], talk['title'])).encode('utf-8'))
        output.write(("%s: <%s>\r\n" % (rooms[i//7], user['email'])).encode('utf-8'))
      

    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/naplnit-newsletter/')
@auth_required
def plneni_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    entrants = get_entrants()
    for entrant in entrants:
        app.redis.sadd('newsletter', entrant['email'])

    return 'omg'


@app.route('/service/poslat-newsletter/')
def poslani_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    for mail in app.redis.smembers('newsletter'):
        print mail
        app.redis.srem('newsletter', mail)

        send_mail(
            u'A je po Barcamp Brno 2015',
            '', #mail,
            'data/newsletter-after.md')

    return 'omg2'


@app.route('/service/test-newsletter/')
def test_newsletteru():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    send_mail(
        u'A je po Barcamp Brno 2015',
        'petr@joachim.cz',
        'data/newsletter-after.md')

    return 'uff'

@app.route('/program-rc/')
def rc_program():
    return render_template(
        'rc-talks.html',
        times=times,
        page_style='program',
        talks=get_talks_dict(),
    )


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

