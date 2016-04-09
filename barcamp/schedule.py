# coding: utf-8

"""
    Schedule settings
"""

from datetime import datetime


schedule = {
    'YEAR': '2016',
    'YEAR_ARCHIVE': ['2013', '2014', '2015'],
    'YEAR_ENABLED': ['2016'],
    'YEAR_SCHEDULE': {
        '2016': {
            'DATE': datetime(2016, 6, 4),
            'STAGES': {
                'PREVIEW': {
                    'from': datetime(1970, 1, 1),
                    'to': datetime(2016, 3, 12),
                },
                'CALL-FOR-PAPERS': {
                    'from': datetime(2016, 3, 13),
                    'to': datetime(2016, 5, 21),
                },
                'CALL-FOR-WORKSHOPS': {
                    'from': datetime(2016, 4, 10),
                    'to': datetime(2016, 5, 21),
                },
            },
        },
        '2017': {
            'DATE': datetime(2017, 6, 3),
            'STAGES': {
                'PREVIEW': {
                    'from': datetime(1970, 1, 1),
                    'to': datetime(2017, 3, 11),
                },
            },
        },
    },
}