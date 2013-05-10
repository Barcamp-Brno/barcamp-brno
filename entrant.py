# coding: utf-8

from barcamp import app
from flask import flash, url_for, redirect, json
from login_misc import check_auth, auth_required, create_update_profile
from time import time

KEYS = {
    'entrant_count': 'entrant_count',  # number
    'entrants': 'entrants',  # sorted set
}


@app.route("/chci-prijit/")
@auth_required
def attend_add():
    user = check_auth()
    if user.get('going', False):
        flash(u'Na akci už jsi byl přihlášen dříve', 'success')
    else:
        user['going'] = True
        create_update_profile(user, user['user_hash'])
        app.redis.zadd(KEYS['entrants'], user['user_hash'], int(time()))
        app.redis.incr(KEYS['entrant_count'])
        flash(u'Nyní jsi přihlášen jako účastník akce', 'success')
    return redirect(url_for('index'))  # , _anchor="entrants"))


@app.route('/nechci-prijit/')
@auth_required
def attend_remove():
    user = check_auth()
    if not user.get('going', False):
        flash(u'Na akci jsi doposud nebyl přihlášen', 'warning')
    else:
        user['going'] = False
        create_update_profile(user, user['user_hash'])
        app.redis.zrem(KEYS['entrants'], user['user_hash'])
        app.redis.decr(KEYS['entrant_count'])
        flash(u'Již nejsi přihlášen na akci', 'success')
    return redirect(url_for('index'))  # , _anchor="entrants"))


def get_count():
    return app.redis.get(KEYS['entrant_count'] or 0)


def get_entrants():
    tuples = app.redis.zrevrange(KEYS['entrants'], 0, -1, withscores=True)
    hashes = [user_tuple[0] for user_tuple in tuples]

    if not hashes:
        return []

    entrants = map(
        lambda user: json.loads(user or 'false'),
        app.redis.mget(map(lambda key: 'account_%s' % key, hashes))
    )
    return entrants
