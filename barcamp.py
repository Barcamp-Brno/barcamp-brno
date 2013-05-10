# coding: utf-8

"""
    Application and settings
"""

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
import redis

app = None


def create_app(config):
    global app
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.update(config)

    app.redis = redis.Redis()

    import views
    import login
    import login_oauth
    import talks
    import entrant
    import vote
    import filters
    import presenters_go
    return app
