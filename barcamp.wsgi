import os
from barcamp import create_app

config = {
    'YEAR': "2015",
    'STAGES': ["INTRO"]
}

config.update(os.environ)

application = create_app(config)
