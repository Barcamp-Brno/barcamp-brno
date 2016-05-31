# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash, render_template, Response
from login_misc import check_auth, auth_required, is_admin
from utils import send_mail
from talks import get_talks_dict, get_talks
from entrant import user_user_go
from collections import defaultdict
from entrant import get_entrants
from datetime import time, date, datetime
from program import times
import requests
import io
import csv

KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
    'eventee': 'eventee_%s' % app.config['YEAR'],
}

@app.route('/service/aplikace')
@auth_required
@is_admin
def fill_eventee_app():
    headers = app.eventee
    redis_key = KEYS['eventee']

    # r = requests.get('https://eventee.co/api/public/all?date=2016-06-01', headers=headers)

    # sync rooms
    rooms = (
        ('d105', u'Prygl'),
        ('e112', u'Špilas'),
        ('d0206', u'Rola'),
        ('d0207', u'Šalina'),
        ('e104', u'Škopek'),
        ('e105', u'Čára'),
        ('a112', u'workshopy'),
        ('a113', u'workshopy'),
        ('c228', u'workshopy'),
    )

    for room, desc in rooms:
        room_key = 'room_%s' % room
        resource_id = app.redis.hget(redis_key, room_key)
        endpoint = 'https://eventee.co/api/public/hall'
        if resource_id:
            endpoint = 'https://eventee.co/api/public/hall/{}'.format(resource_id)
        data = {
            'name': u'{} {}'.format(room.upper(), desc)
        }
        response = requests.post(
            endpoint,
            json=data,
            headers=headers
        )
        status = response.json()
        app.redis.hset(redis_key, room_key, int(status['id']))
        print data, endpoint, status

    # sync breaks
    for t in times:
        if type(t['data']) is not dict:
            print t['data']

    # sync talks & speakers

    return Response("ok", mimetype="text/plain")


@app.route('/service/program-mistnosti')
@auth_required
@is_admin
def room_program():
    output = io.BytesIO()
    writer = csv.writer(output, delimiter=";", dialect="excel", quotechar='"')
    writer.writerow([
        'room',
        'title',
        'name'
        'from',
        'to',
        'next_title',
        'next_name',
        'next_from',
        'next_to',
    ])
    talk_hashed = get_talks_dict()

    for room in ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105'):
        talks = []
        for i, t in enumerate(times):
            if type(t['data']) is dict and t['data'][room] in talk_hashed:
                talk = talk_hashed.get(t['data'][room], None)
            else:
                continue

            talks.append([
                talk['title'],
                talk['user']['name'],
                t['block_from'].strftime('%H:%M'),
                t['block_to'].strftime('%H:%M')
            ])

        for i in range(len(talks)):
            if i == len(talks) - 1:
                _ = [room] + talks[i] + ['', '', '', '']
            else:
                _ = [room] + talks[i] +  talks[i+1]
            writer.writerow([unicode(s).encode("utf-8") for s in _])

    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/vyvoleni')
@auth_required
@is_admin
def service_vyvoleni():
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
@is_admin
def service_do_programu():
    talks, extra_talks = get_talks()
    talks = talks[:42]
    output = io.BytesIO()
    
    rooms =  'd105', 'e112', 'd0206', 'd0207', 'e104', 'e105'
    for i, talk in enumerate(talks):
        user = talk['user']
        #output.write(("'%s': '%s', # %sx %s / %s \r\n" % (rooms[i//7], talk['talk_hash'], talk['score'], user['name'], talk['title'])).encode('utf-8'))
        output.write(("%s: <%s>\r\n" % (rooms[i//7], user['email'])).encode('utf-8'))
      

    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/naplnit-newsletter/')
@auth_required
@is_admin
def plneni_newsletteru():
    entrants = get_entrants()
    for entrant in entrants:
        app.redis.sadd('newsletter', entrant['email'])

    return 'omg'


@app.route('/service/poslat-newsletter/')
@auth_required
@is_admin
def poslani_newsletteru():
    for mail in app.redis.smembers('newsletter'):
        print mail
        app.redis.srem('newsletter', mail)

        send_mail(
            u'A je po Barcamp Brno 2015',
            '', #mail,
            'data/newsletter-after.md')

    return 'omg2'


@app.route('/service/test-newsletter/')
@auth_required
@is_admin
def test_newsletteru():
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
@is_admin
def prepocet_hlasu():
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

