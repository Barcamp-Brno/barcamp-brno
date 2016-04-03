import os
from barcamp import create_app, schedule

config = {
    'MAIL_SERVER': 'smtp.sendgrid.net',
    'MAIL_PORT': 587,
    'MAIL_USERNAME': os.environ.get('SENDGRID_USERNAME', ''),
    'MAIL_PASSWORD': os.environ.get('SENDGRID_PASSWORD', ''),
}

config.update(schedule)
config.update(os.environ)

application = create_app(config)
