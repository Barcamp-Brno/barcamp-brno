# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash, render_template, Response
from login_misc import check_auth, auth_required, is_admin
from utils import send_mail
from talks import get_talks_dict, get_talks
from workshops import get_workshops_dict
from entrant import user_user_go
from collections import defaultdict
from entrant import get_entrants
from datetime import time, date, datetime
from program import times
from copy import copy
from pprint import pprint
import requests
import io
import csv
import re

KEYS = {
    'talk': 'talk_%s_%%s' % app.config['YEAR'],
    'talks': 'talks_%s' % app.config['YEAR'],
    'extra': 'extra_talks_%s' % app.config['YEAR'],
    'eventee': 'eventee_%s' % app.config['YEAR'],
}

ENDPOINT = {
    'break': 'https://eventee.co/api/public/break',
    'room': 'https://eventee.co/api/public/hall',
    'talk': 'https://eventee.co/api/public/lecture',
    'speaker': 'https://eventee.co/api/public/user/register/speaker',
}

@app.route('/service/aplikace')
@auth_required
@is_admin
def fill_eventee_app():
    headers = app.eventee
    redis_key = KEYS['eventee']
    ids = {
        'breaks': [],
        'rooms': [],
        'talks': [],
        'speakers': [],
    }

    data = requests.get('https://eventee.co/api/public/all?date=2016-06-04', headers=headers)
    data = data.json()

    for hall in data['halls'].values():
        ids['rooms'].append(hall['id'])
        if type(hall['lectures']) is dict:
            for lecture in hall['lectures'].values():
                ids['talks'].append(lecture['id'])

    for b in data['breaks'].values():
        ids['breaks'].append(b['id'])

    for lecturer in data['lecturers'].values():
        ids['speakers'].append(lecturer['id'])

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
        ('Hyde', 'Park'),
    )

    for room, desc in rooms:
        room_key = 'room_%s' % room
        resource_id = app.redis.hget(redis_key, room_key)
        endpoint = ENDPOINT['room']
        if resource_id:
            ids['rooms'].remove(int(resource_id))
            endpoint = '{}/{}'.format(endpoint, resource_id)
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

    for room_id in ids['rooms']:
        endpoint = "{}/{}".format(ENDPOINT['room'], room_id)
        requests.delete(endpoint, headers=headers)

    # sync breaks
    for t in times:
        if type(t['data']) is not dict:
            break_key = 'break_{}_{}'.format(t['date'], t['block_from'])
            endpoint = ENDPOINT['break']
            resource_id = app.redis.hget(redis_key, break_key)

            if resource_id:
                ids['breaks'].remove(int(resource_id))
                endpoint = "{}/{}".format(endpoint, resource_id)
            data = {
                'name': re.sub('<[^<]+?>', '', t['data']),
                'start': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_from']),
                'end': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_to']),
            }
            response = requests.post(
                endpoint,
                json=data,
                headers=headers
            )
            status = response.json()
            app.redis.hset(redis_key, break_key, int(status['id']))

    for break_id in ids['breaks']:
        endpoint = "{}/{}".format(ENDPOINT['break'], break_id)
        requests.delete(endpoint, headers=headers)


    # sync talks & speakers
    talk_rooms = ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105')
    workshop_rooms = ('a112', 'a113', 'c228')
    talks = get_talks_dict()
    workshops = get_workshops_dict()
    _shit_re = re.compile(r'[^\w .-/?!,()*\n\r]+', re.UNICODE)
    _spaces = re.compile(r'\s\s+')
    explode_speakers = ('bea84558', 'f89ae7e6')
    def clear(s):
        s = _shit_re.sub('', s)
        s = _spaces.sub(' ', s)
        return s.strip()

    i = 0
    for t in times:
        if type(t['data']) is not dict:
            continue

        for room in talk_rooms + workshop_rooms:
            room_id = app.redis.hget(redis_key, 'room_%s' % room)
            h = t['data'].get(room, False)
            if not h:
                continue

            if room in talk_rooms:
                lecture = talks.get(h, False)
                hash_key = 'talk_hash'
            else:
                lecture = workshops.get(h, False)
                hash_key = 'workshop_hash'

            if not lecture:
                continue

            speakers = [lecture['user']]

            if h in explode_speakers:
                words = speakers[0]['name'].split(' ')
                speaker1 = copy(speakers[0])
                speaker1['name'] = ' '.join(words[0:2])
                speaker1['user_hash'] += '_1'
                speaker2 = copy(speakers[0])
                speaker2['name'] = ' '.join(words[3:5])
                speaker2['user_hash'] += '_2'
                speakers = [speaker1, speaker2]

            speaker_ids = []

            for speaker in speakers:
                speaker_key = 'speaker_{}'.format(speaker['user_hash'])
                resource_id = app.redis.hget(redis_key, speaker_key)
                if not resource_id:
                    endpoint = ENDPOINT['speaker']
                    data = {
                        'name': clear(speaker['name']),
                        'bio': '',
                    }
                    response = requests.post(
                        endpoint,
                        json=data,
                        headers=headers
                    )
                    status = response.json()
                    resource_id = int(status['id'])
                    app.redis.hset(redis_key, speaker_key, resource_id)
                speaker_ids.append(resource_id)

            #talk
            talk_key = "talk_{}".format(lecture[hash_key])
            endpoint = ENDPOINT['talk']
            resource_id = app.redis.hget(redis_key, talk_key)

            if resource_id:
                ids['talks'].remove(int(resource_id))
                endpoint = "{}/{}".format(endpoint, resource_id)

            data = {
                'name': clear(lecture['title']),
                'description': clear(lecture['description']),
                'start': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_from']),
                'end': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_to']),
                'speakers': speaker_ids,
                'hallId': room_id,
            }

            response = requests.post(
                endpoint,
                json=data,
                headers=headers
            )
            status = response.json()
            app.redis.hset(redis_key, talk_key, int(status['id']))

    for talk_id in ids['talks']:
        endpoint = "{}/{}".format(ENDPOINT['talk'], talk_id)
        requests.delete(endpoint, headers=headers)

    return Response("ok", mimetype="text/plain")


@app.route('/service/program-mistnosti')
@auth_required
@is_admin
def room_program():
    output = io.BytesIO()
    writer = csv.writer(output, delimiter=",", dialect="excel", quotechar='"')
    writer.writerow([
        'room',
        'room_name',
        'title',
        'name',
        'from',
        'to',
        'next_title',
        'next_name',
        'next_from',
        'next_to',
    ])
    talk_hashed = get_talks_dict()

    rooms = (
        ('d105', u'Prygl'),
        ('e112', u'Špilas'),
        ('d0206', u'Rola'),
        ('d0207', u'Šalina'),
        ('e104', u'Škopek'),
        ('e105', u'Čára'),
    )

    for room, room_name in rooms:
        talks = []
        for i, t in enumerate(times):
            if type(t['data']) is dict:
                if t['data'][room] in talk_hashed:
                    talk = talk_hashed.get(t['data'][room], None)
                else:
                    talks.append([
                        '','', 
                        t['block_from'].strftime('%H.%M'),
                        t['block_to'].strftime('%H.%M')])
                    continue
            else:
                continue

            talks.append([
                talk['title'],
                talk['user']['name'],
                t['block_from'].strftime('%H.%M'),
                t['block_to'].strftime('%H.%M')
            ])

        for i in range(len(talks)):
            if i == len(talks) - 1:
                _ = [room.upper(), room_name] + talks[i] + ['', '', '', '']
            else:
                _ = [room.upper(), room_name] + talks[i] +  talks[i+1]
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

@app.route('/service/bad-luck')
@auth_required
@is_admin
def service_bad_luck():
    talks, extra_talks = get_talks()
    talks = talks[42:]
    output = io.BytesIO()
    
    for i, talk in enumerate(talks):
        user = talk['user']
        #output.write(("'%s': '%s', # %sx %s / %s \r\n" % (rooms[i//7], talk['talk_hash'], talk['score'], user['name'], talk['title'])).encode('utf-8'))
        output.write(("%s <%s>: %s\r\n" % (user['name'], user['email'], talk['title'])).encode('utf-8'))
      

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

