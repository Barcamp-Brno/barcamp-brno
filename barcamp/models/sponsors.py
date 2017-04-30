# coding: utf-8
import json
from collections import defaultdict

from flask_wtf import Form
from wtforms import TextField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, URL, Optional, NumberRange

KEYS = {
    'sponsor': 'sponsor_%s_%%s',
    'sponsors': 'sponsors_%s',
}

class Sponsors():
    def __init__(self, redis, year):
        self._redis = redis
        self._year = year
        self.KEYS = {
            'sponsor': 'sponsor_%s_%%s' % year,
            'sponsors': 'sponsors_%s' % year,
        }

    def get_all(self):
        sponsor_members = self._redis.zrevrange(self.KEYS['sponsors'], 0, -1, True)
        sponsor_dict = dict(sponsor_members)
        if not len(sponsor_members):
            return tuple()

        sponsors = filter( # filter out invalid
            lambda x: bool(x),
            map( # load json into Python dict
                lambda sponsor: json.loads(sponsor or 'false'),
                self._redis.mget([data[0] for data in sponsor_members])
            )
        )

        print(sponsors)

        for sponsor in sponsors:
            sponsor['score'] = sponsor_dict[self.KEYS['sponsor'] % sponsor['uri']]

        return sponsors

    def get_all_by_type(self):
        sponsors = self.get_all()
        sponsors_dict = defaultdict(list)
        for sponsor in sponsors:
            sponsors_dict[sponsor['sponsorship']].append(sponsor)

        return sponsors_dict

    def get_posible_routes(self):
        return [sponsor['uri'] for sponsor in self.get_all()]

    def get(self, uri):
        if not self._redis.exists(self.KEYS['sponsor'] % uri):
            return False

        return json.loads(self._redis.get(self.KEYS['sponsor'] % uri))

    def update(self, data):
        url = data['uri']
        self._redis.zadd(self.KEYS['sponsors'], self.KEYS['sponsor'] % data['uri'], data['score'])
        self._redis.set(self.KEYS['sponsor'] % data['uri'], json.dumps(data))
        return data

    def delete(self, uri):
        self._redis.zrem(self.KEYS['sponsors'], self.KEYS['sponsor'] % uri)
        return self._redis.delete(self.KEYS['sponsor'] % uri)

class SponsorForm(Form):
    title = TextField(u'Nazev', validators=[DataRequired()])
    uri = TextField(u'Slug', validators=[DataRequired()], widget=TextAreaField())
    action_url = TextField(u'Url společnosti', validators=[DataRequired()])
    score = TextField(u'Váha', validators=[DataRequired(), NumberRange()], default=1)

    sponsorship = RadioField(
        u'Typ sponzorství',
        choices=[
            (u'gold', u'Zlatý'),
            (u'silver', u'Stříbrný'),
            (u'social', u'Sociální'),
            (u'medial', u'Mediální'),
            (u'catering', u'Catering'),
            (u'other', u'Ostatní'),
        ],
        validators=[DataRequired()],
        default='other',
    )

    logo =  TextField(
        u'Kód loga',
        validators=[DataRequired()],
        default='[![XXX](https://barcamp-brno.github.io/static/partners/ "XXX")](http://xx.xxx)',
    )

    activity_body = TextField(
        u'Popis aktivity',
        validators=[],
        widget=TextAreaField(),
    )

    body = TextField(
        u'Popis společnosti',
        validators=[],
        widget=TextAreaField(),
    )