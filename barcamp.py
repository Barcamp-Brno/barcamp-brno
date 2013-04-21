# coding: utf-8

"""
    Application and settings
"""

from flask import Flask
import redis

app = None


def create_app(config):
    global app
    application = Flask(__name__)
    application.secret_key = "jednadvehonzajde"
    application.config.update(config)

    application.redis = redis.Redis()

    app = application

    import views
    import login
    import talks
    import filters
    return app
