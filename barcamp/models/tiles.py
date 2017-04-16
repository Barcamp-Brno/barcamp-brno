# coding: utf-8
import json
from uuid import uuid1 as uuid

from flask_wtf import Form
from wtforms import TextField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, URL, Optional, NumberRange
from ..schedule import schedule
from ..barcamp import app


class Tiles():
    def __init__(self, redis, year):
        self._redis = redis
        self._year = year
        self.KEYS = {
            'tile': 'tile_%s_%%s' % year,
            'tiles': 'tiles_%s' % year,
        }

    def get_all(self):
        tile_members = self._redis.zrevrange(self.KEYS['tiles'], 0, -1, True)
        tile_dict = dict(tile_members)
        if not len(tile_members):
            return tuple()

        tiles = filter( # filter out invalid
            lambda x: bool(x),
            map( # load json into Python dict
                lambda tile: json.loads(tile or 'false'),
                self._redis.mget([idx[0] for idx in tile_members])
            )
        )

        for tile in tiles:
            tile['score'] = tile_dict[self.KEYS['tile'] % tile['idx']]

        return tiles

    def get(self, idx):
        if not self._redis.exists(self.KEYS['tile'] % idx):
            return False

        return json.loads(self._redis.get(self.KEYS['tile'] % idx))

    def update(self, data):
        if 'idx' not in data:
            data['idx'] = uuid().hex
        
        self._redis.zadd(self.KEYS['tiles'], self.KEYS['tile'] % data['idx'], data['score'])
        self._redis.set(self.KEYS['tile'] % data['idx'], json.dumps(data))
        return data

    def delete(self, idx):
        self._redis.zrem(self.KEYS['tiles'], self.KEYS['tile'] % idx)
        return self._redis.delete(self.KEYS['tile'] % idx)


def _get_choices(year):
    return [
        (key, "{}: od {} do {}".format(
            key,
            value['from'].strftime('%Y-%m-%d'),
            value["to"].strftime('%Y-%m-%d')),
        )
        for key, value in schedule['YEAR_SCHEDULE'][year]['STAGES'].items()
    ]

class TileForm(Form):
    title = TextField(u'Titulek', validators=[DataRequired()])
    score = TextField(u'Váha', validators=[DataRequired(), NumberRange()], default=1)
    body = TextField(
        u'Obsah',
        validators=[],
        widget=TextAreaField(),
    )

    action_caption = TextField(u'Caption', validators=[DataRequired()])
    action_icon = TextField(
        u'Fontawesome icon',
        validators=[DataRequired()],
        default=u'fa-hand-o-right',
    )
    action_class = TextField(
        u'Bootstrap button class',
        validators=[DataRequired()],
        default=u'btn-danger',
    )
    action_url = TextField(u'Url', validators=[DataRequired()])

    visible_from = RadioField(
        u'Viditelné od',
        choices=_get_choices(app.config['YEAR']),
        validators=[DataRequired()],
        default='PREVIEW',
    )
    visible_after_stage = BooleanField(
        u'Bude vidět i po té době',
        default=True)




