# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash, render_template, Response
from login_misc import check_auth, auth_required, is_admin
from utils import send_mail, send_bulk_mail, mail_bulk_connection
from talks import get_talks_dict, get_talks, get_talks_by_type, CATEGORIES, translate_category
from workshops import get_workshops_dict
from entrant import user_user_go
from collections import defaultdict
from entrant import get_entrants
from datetime import time, date, datetime, timedelta
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

    data = requests.get('https://eventee.co/api/public/all?date=2017-06-03', headers=headers)
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
        print(data['name'])
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

            print(data['name'])
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
    explode_speakers = ()
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
            hashes = t['data'].get(room, False)
            if not hashes:
                continue

            if type(hashes) == dict:
                # process lighning talks

                # speaker
                speaker_key = 'speaker_barcamp'
                resource_id = app.redis.hget(redis_key, speaker_key)
                speaker_ids = []
                if not resource_id:
                    print("Barcamp Brno")
                    endpoint = ENDPOINT['speaker']
                    data = {
                        'name': "Barcamp Brno",
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

                #lightning talk
                talk_key = "talk_lightning_{}".format(hashes['category'])
                endpoint = ENDPOINT['talk']
                resource_id = app.redis.hget(redis_key, talk_key)

                if resource_id:
                    ids['talks'].remove(int(resource_id))
                    endpoint = "{}/{}".format(endpoint, resource_id)

                data = {
                    'name': u"Lightning talky ({})".format(translate_category(hashes['category'])),
                    'description': "",
                    'start': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_from']),
                    'end': '{} {}'.format(t['date'].strftime('%Y-%m-%d'), t['block_to']),
                    'speakers': speaker_ids,
                    'hallId': room_id,
                }

                print(data['name'])

                response = requests.post(
                    endpoint,
                    json=data,
                    headers=headers
                )
                status = response.json()
                app.redis.hset(redis_key, talk_key, int(status['id']))

                continue

            if room not in talk_rooms:
                hashes = (hashes, )

            for i, h in enumerate(hashes):
                if room in talk_rooms:
                    lecture = talks.get(h, False)
                    hash_key = 'talk_hash'
                else:
                    lecture = workshops.get(h, False)
                    hash_key = 'workshop_hash'

                if not lecture:
                    print("missing {} {}".format(room, h))
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
                    print speaker['name']
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

                print(data['name'])

                if room in workshop_rooms:
                    minutes = 45 if lecture['minutes'] <= 60 else 105
                    end = datetime.combine(t['date'], t['block_from']) + timedelta(minutes=minutes)
                    data['end'] = str(end)

                if len(hashes) > 1 and i == 0:
                    data['end'] = str(datetime.combine(t['date'], t['block_to']) - timedelta(minutes=22))
                if len(hashes) > 1 and i == 1:
                    data['start'] = str(datetime.combine(t['date'], t['block_from']) + timedelta(minutes=22))

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


@app.route('/service/speakers-mails/')
@auth_required
@is_admin
def service_speaker_mail():
    talk_hashed = get_talks_dict()
    talks = []
    for t in times:
        if type(t['data']) is dict:
            for room in ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105'):
                talk = talk_hashed.get(t['data'][room], None)
                if talk:
                    talks.append(talk)
    workshop_hashed = get_workshops_dict()
    workshops = []
    for t in times:
        if type(t['data']) is dict:
            for room in ('a112', 'a113', 'c228'):
                workshop = workshop_hashed.get(t['data'][room], None)
                if workshop:
                    workshops.append(workshop)

    output = io.BytesIO()
    writer = csv.writer(output, delimiter=";", dialect="excel", quotechar='"')
    for lecture in talks + workshops:
        writer.writerow([lecture['user']['email']])

    return Response(output.getvalue(), mimetype="text/plain")


def service_vyvoleni(_format):
    # talks, extra_talks = get_talks()
    talk_hashed = get_talks_dict()
    talks = []
    for t in times:
        if type(t['data']) is dict:
            for room in ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105'):
                if type(t['data'][room]) is tuple:
                    for h in t['data'][room]:
                        talk = talk_hashed.get(h, None)
                        if talk:
                            talk['room'] = room
                            talks.append(talk)

    output = io.BytesIO()

    if _format == "csv":
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
    else:
        for talk in talks:
            output.write(("%s: <%s>\r\n" % (talk['room'], talk['user']['email'])).encode('utf-8'))

    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/vyvoleni')
@auth_required
@is_admin
def service_vyvoleni_csv():
    return service_vyvoleni('csv')

@app.route('/service/maily-prednasejicich')
@auth_required
@is_admin
def service_maily_prednasejicich():
    return service_vyvoleni('emails')

@app.route('/service/do-programu')
@auth_required
@is_admin
def service_do_programu():
    talks = get_talks_by_type()
    output = io.BytesIO()
    
    categories =  [c[0] for c in CATEGORIES]

    for category in categories:
        total = 0
        for i, talk in enumerate(talks[category]):
            if total > 8 * 45:
                break
            user = talk['user']
            output.write(("'%s', # %s %s %sx %s / %s \r\n" % (talk['talk_hash'], category, talk['length'], talk['score'], user['name'], talk['title'])).encode('utf-8'))
            total += int(talk['length'])

    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/bad-luck')
@auth_required
@is_admin
def service_bad_luck():

    talk_hashed = get_talks_dict()
    for t in times:
        if type(t['data']) is dict:
            for room in ('d105', 'd0206', 'd0207', 'e112', 'e104', 'e105'):
                if type(t['data'][room]) is tuple:
                    for h in t['data'][room]:
                        if h in talk_hashed:
                            del talk_hashed[h]

    output = io.BytesIO()
    
    for i, talk in enumerate(talk_hashed.values()):
        user = talk['user']
        output.write(("<%s>\r\n" % (user['email'])).encode('utf-8'))
      
    return Response(output.getvalue(), mimetype="text/plain")

@app.route('/service/naplnit-newsletter/')
@auth_required
@is_admin
def plneni_newsletteru():
    entrants = get_entrants()
    for entrant in entrants:
        app.redis.sadd('newsletter', entrant['email'])

    return 'filled {} entrants'.format(len(entrants))


@app.route('/service/poslat-newsletter/')
@auth_required
@is_admin
def poslani_newsletteru():
    i = 0
    with mail_bulk_connection() as conn:
        for mail in app.redis.smembers('newsletter'):
            i += 1
            print mail
            app.redis.srem('newsletter', mail)

            send_bulk_mail(
                conn,
                u'Hodně budem někde - Barcamp Brno 2017',
                mail,
                'data/newsletter-reminder.md')


    return 'newsletter done {} emails'.format(i)


@app.route('/service/test-newsletter/')
@auth_required
@is_admin
def test_newsletteru():
    send_mail(
        u'Hodně budem někde - Barcamp Brno 2017',
        'petr@joachim.cz',
        'data/newsletter-reminder.md')

    return 'done'

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

