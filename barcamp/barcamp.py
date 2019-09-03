# coding: utf-8

"""
    Application and settings
"""

from flask import Flask
from werkzeug.routing import Rule

import redis
import sentry_sdk
import mailchimp
from sentry_sdk.integrations.flask import FlaskIntegration


app = None

class GeneratorRule(Rule):
    def __init__(self, rule, **kwargs):
        self.generator = kwargs.get('generator', None)
        if self.generator:
            kwargs.pop('generator')

        super(GeneratorRule, self).__init__(rule, **kwargs)

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

def create_app(config):
    global app
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.update(config)

    app.url_rule_class = GeneratorRule

    app.redis = redis.Redis.from_url(config['REDISCLOUD_URL'], decode_responses=True)
    app.eventee = {
        'token': config['EVENTEE_TOKEN'],
        'email': config['EVENTEE_EMAIL'],
    }

    if config.get('FLASK_ENV', 'production') == 'production':
        sentry_sdk.init(
            dsn=config['SENTRY_DSN'],
            integrations=[FlaskIntegration()]
        )

    from . import views
    from . import login
    from . import login_oauth
    from . import talks
    from . import program
    from . import entrant
    from . import vote
    from . import filters
    from . import service
    from . import workshops

    from .admin import admin

    app.register_blueprint(admin, url_prefix='/admin')
    return app
