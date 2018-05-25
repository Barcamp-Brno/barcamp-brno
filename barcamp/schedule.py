# coding: utf-8

"""
    Schedule settings
"""

from datetime import datetime


schedule = {
    'YEAR': '2018',
    'YEAR_ARCHIVE': ['2013', '2014', '2015', '2016', '2017'],
    'YEAR_ENABLED': ['2018'],
    'YEAR_SCHEDULE': {
        # '2016': {
        #     'DATE': datetime(2016, 6, 4),
        #     'STAGES': {
        #         'T-SHIRTS': {
        #             'from': datetime(2016, 4, 22),
        #             'to': datetime(2016, 5, 13),
        #         },
        #         'PROGRAM': {
        #             'from': datetime(2016, 5, 29),
        #             'to': datetime(2020, 12, 31),
        #         },
        #         'PROGRAM-MENU': {
        #             'from': datetime(2016, 5, 29),
        #             'to': datetime(2020, 6, 4),
        #         },
        #         'REVIEW-MENU': {
        #             'from': datetime(2016, 6, 15),
        #             'to': datetime(2020, 6, 4),
        #         }
        #     },
        # },
        '2018': {
            'DATE': datetime(2018, 6, 2),
            'STAGES': {
                'PREVIEW': {
                    'from': datetime(1970, 1, 1),
                    'to': datetime(2018, 2, 11),
                },
                'CALL-FOR-PAPERS': {
                    'from': datetime(2018, 4, 1),
                    'to': datetime(2018, 5, 21),
                },
                'CALL-FOR-WORKSHOPS': {
                    'from': datetime(2018, 4, 1),
                    'to': datetime(2018, 5, 21),
                },
                'VOTING': {
                    'from': datetime(2018, 5, 1),
                    'to': datetime(2018, 5, 21),
                },
                'WORKSHOPS-PROGRAM': {
                    'from': datetime(2018, 5, 23),
                    'to': datetime(2021, 12, 31),
                },
                'PROGRAM': {
                    'from': datetime(2018, 5, 24),
                    'to': datetime(2021, 12, 31),
                },
                'USERS': {
                    'from': datetime(2018, 5, 1),
                    'to': datetime(2018, 6, 3),
                },
            },
            
        },
    },
}