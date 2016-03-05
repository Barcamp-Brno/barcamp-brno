# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash
from login_misc import check_auth, auth_required
from talks import get_talks
from entrant import user_user_go

@app.route("/vsichni-jsou-uz-v-mexiku/")
@auth_required
def mexico_tequilla():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    talks = get_talks()
    for talk in talks:
        user_user_go(talk['user'])

    flash(u'Prezentující přidáni jako účastníci')
    return redirect(url_for('index'))
