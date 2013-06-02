# coding: utf-8

from barcamp import app
from flask import flash, url_for, redirect, request
from login_misc import check_auth, auth_required

KEYS = {
    'votes': 'votes_%s',  # set
}


@app.route('/zmenit-hlasy/', methods=['POST'])
@auth_required
def vote_save():
    flash(u'Hlasování bylo ukončeno', 'warning')
    return redirect(url_for('index'))
    user = check_auth()
    user_hash = user['user_hash']
    old_votes = app.redis.smembers(KEYS['votes'] % user_hash) or set()
    new_votes = set([item[0] for item in request.form.items()])

    increment = new_votes - old_votes
    decrement = old_votes - new_votes
    # stand_still = old_votes & new_votes

    for vote in increment:
        app.redis.sadd(KEYS['votes'] % user_hash, vote)
        app.redis.zincrby('talks', vote, 1)

    for vote in decrement:
        app.redis.srem(KEYS['votes'] % user_hash, vote)
        app.redis.zincrby('talks', vote, -1)

    flash(u'Hlasy byly uloženy', 'success')
    return redirect(url_for('index'))


def get_user_votes(user_hash):
    return tuple(app.redis.smembers(KEYS['votes'] % user_hash))


def remove_user_votes(user_hash):
    decrement = app.redis.smembers(KEYS['votes'] % user_hash) or set()
    for vote in decrement:
        app.redis.srem(KEYS['votes'] % user_hash, vote)
        app.redis.zincrby('talks', vote, -1)
