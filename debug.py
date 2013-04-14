#!/usr/bin/python
# coding: utf-8

"""
    DEBUG application urls :)

    https://developers.facebook.com/apps/536796489696963
    https://dev.twitter.com/apps/4291778/show
"""

from barcamp import create_app

if __name__ == '__main__':
    app = create_app({
        'FACEBOOK_ID': '536796489696963',
        'FACEBOOK_SECRET': '1203f3bd7633d102e30cc02f7d61b3f8',
        'TWITTER_KEY': 'H3YBefguk72B38Yt5KdDg',
        'TWITTER_SECRET': 'cPmxDXCm3MgVPruiCjYXioZhUubLvehnTiVgI1M',
    })

    app.debug = True
    app.run("0", 8888)
