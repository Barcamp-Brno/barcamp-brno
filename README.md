Barcamp Brno
============
Webová aplikace řešící organizování Barcamp Brno 2013+

Requirements
------------

 - git
 - python 2.7
 - pip
 - heroku toolbelt
 - npm


Debug
-----

 - `heroku config -s > .env`
 - `pip install -r requirements.txt`
 - `npm install`
 - `grunt`
 - `heroku local:run python debug.py`

Deploy
------

 - `git push heroku master`