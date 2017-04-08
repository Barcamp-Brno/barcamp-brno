import json

from flask_wtf import Form
from wtforms import TextField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, URL, Optional

KEYS = {
    'page': 'page_%s_%%s',
    'pages': 'pages_%s',
}

class Pages():
    def __init__(self, redis, year):
        self._redis = redis
        self._year = year
        self.KEYS = {
            'page': 'page_%s_%%s' % year,
            'pages': 'pages_%s' % year,
        }

    def get_all(self):
        page_members = self._redis.smembers(self.KEYS['pages'])
        if not len(page_members):
            return tuple()

        pages = filter( # filter out invalid
            lambda x: bool(x),
            map( # load json into Python dict
                lambda page: json.loads(page or 'false'),
                self._redis.mget(page_members)
            )
        )
        return pages

    def get_posible_routes(self):
        return [page['uri'] for page in self.get_all()]

    def get(self, uri):
        if not self._redis.exists(self.KEYS['page'] % uri):
            return False

        return json.loads(self._redis.get(self.KEYS['page'] % uri))

    def update(self, data):
        url = data['uri']
        self._redis.sadd(self.KEYS['pages'], self.KEYS['page'] % data['uri'])
        self._redis.set(self.KEYS['page'] % data['uri'], json.dumps(data))
        return data

    def delete(self, uri):
        self._redis.srem(self.KEYS['pages'], self.KEYS['page'] % uri)
        return self._redis.delete(self.KEYS['page'] % uri)

class PageForm(Form):
    title = TextField(u'Titulek', validators=[DataRequired()])
    uri = TextField(u'Url', validators=[DataRequired()])
    body = TextField(
        u'Obsah',
        validators=[],
        widget=TextAreaField(),
    )