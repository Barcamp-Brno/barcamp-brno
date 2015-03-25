import os
from barcamp import create_app

config = {
    'YEAR': "2015",
    'STAGES': ["INTRO"],
    'MAIL_SERVER': 'smtp.mandrillapp.com',
    'MAIL_PORT': 587,
    'MAIL_USERNAME': os.environ.get('MANDRILL_USERNAME', ''),
    'MAIL_PASSWORD': os.environ.get('MANDRILL_APIKEY', ''),
}

config.update(os.environ)

application = create_app(config)
