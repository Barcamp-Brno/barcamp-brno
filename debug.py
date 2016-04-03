#!/usr/bin/python
# coding: utf-8

"""
    DEBUG application urls :)

    https://developers.facebook.com/apps/536796489696963
    https://dev.twitter.com/apps/4291778/show
"""

from barcamp import create_app, schedule
from datetime import datetime
import os

if __name__ == '__main__':
    config = {
        'FACEBOOK_ID': '',
        'FACEBOOK_SECRET': '',
        'TWITTER_KEY': '',
        'TWITTER_SECRET': '',
        'TESTING': False,
        'SECRET_KEY': 'jednadvehonzajde',
        'MAIL_SERVER': 'smtp.sendgrid.net',
        'MAIL_PORT': 587,
        'MAIL_USERNAME': os.environ.get('SENDGRID_USERNAME', ''),
        'MAIL_PASSWORD': os.environ.get('SENDGRID_PASSWORD', ''),
        'TEST_DATE': datetime(2016, 3, 13),
    }

    config.update(schedule)
    config.update(os.environ)
    app = create_app(config)

    # app.debug = True
    app.run("0", 9099)
