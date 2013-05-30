
# coding: utf-8

from barcamp import app
from flask import abort, redirect, url_for, flash
from login_misc import check_auth, auth_required
from talks import get_talks
from entrant import user_user_go


@app.route("/jedna-dve-tri-ctyri-pet/")
@auth_required
def prepocet_hlasu():
    user = check_auth()
    if user['email'] != u'petr@joachim.cz':
        abort(418)

    return redirect(url_for('index'))
