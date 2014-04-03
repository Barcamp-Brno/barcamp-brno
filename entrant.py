# coding: utf-8

from barcamp import app
from flask import flash, url_for, redirect, json
from login_misc import check_auth, auth_required, create_update_profile
from vote import remove_user_votes
from time import time

KEYS = {
    'entrant_count': 'entrant_count_%s' % app.config['YEAR'],  # number
    'entrants': 'entrants_%s' % app.config['YEAR'],  # sorted set
}


@app.route("/chci-prijit/")
@auth_required
def attend_add():
    user = check_auth()
    if user_user_go(user):
        flash(u'Na akci už jsi byl přihlášen dříve', 'success')
    else:
        flash(u'Nyní jsi přihlášen jako účastník akce', 'success')
    return redirect(url_for('index'))  # , _anchor="entrants"))


def user_user_go(user):
    if user.get('going_%s' % app.config['YEAR'], False):
        return True
    else:
        user['going'] = True
        create_update_profile(user, user['user_hash'])
        app.redis.zadd(KEYS['entrants'], user['user_hash'], int(time()))
        app.redis.incr(KEYS['entrant_count'])
        return False


@app.route('/nechci-prijit/')
@auth_required
def attend_remove():
    user = check_auth()
    if not user.get('going_%s' % app.config['YEAR'], False):
        flash(u'Na akci jsi doposud nebyl přihlášen', 'warning')
    else:
        user['going_%s' % app.config['YEAR']] = False
        create_update_profile(user, user['user_hash'])
        app.redis.zrem(KEYS['entrants'], user['user_hash'])
        app.redis.decr(KEYS['entrant_count'])
        remove_user_votes(user['user_hash'])
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
