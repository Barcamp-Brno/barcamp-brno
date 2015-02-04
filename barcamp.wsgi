import os
from barcamp import create_app

config = {
    'YEAR': "2014",
    'STAGES': ['PROGRAM_READY', 'END']
}

config.update(os.environ)

application = create_app(config)
