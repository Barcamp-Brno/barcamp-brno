from barcamp import create_app

application = create_app({
    'YEAR': "2014",
    'STAGES': ['PROGRAM_READY', 'END']
})
