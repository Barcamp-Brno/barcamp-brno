#!/usr/bin/python

import re
import os
from barcamp import create_app

PUBLISH_SKIP_URLS = (
    '/static/.*',
    '.*/$'
)
PUBLISH_ADD_FILES = (
    'static',
)

YEAR = "2013"

class Publisher(object):
    def __init__(self, app):
        self.app = app

    def __rip_page(self, url):
        client = app.test_client()
        response = client.get(url)

        return response.data

    def __get_rules(self):
        if PUBLISH_SKIP_URLS:
            rules = [rule for rule in self.app.url_map.iter_rules() if (
                not any([re.match(r, rule.rule) for r in PUBLISH_SKIP_URLS])
            )]
        else:
            rules = [rule for rule in self.app.url_map.iter_rules()]

        return rules

    def __get_urls(self):
        for rule in self.__get_rules():
            if rule.alias:
                print "skip alias: %s" % rule.rule
                continue

            if rule.arguments:
                if rule.generator:
                    for param in rule.generator():
                        yield rule.build(param)[1]
                else:
                    print "missing generator for rule %s" % rule.rule
            else:
                yield rule.rule

    def __create_dir_recursively_if_not_exists(self, dir):
        if os.path.exists(dir):
            return

        if dir:
            base, chunk = os.path.split(dir)
            self.__create_dir_recursively_if_not_exists(base)
            os.mkdir(dir)

    def __save_page(self, url, storage_path):
        filename = "%s%s" % (os.path.dirname(storage_path), url)
        print "saving url: %s to file %s" % (url, filename)
        data = self.__rip_page(url)

        self.__create_dir_recursively_if_not_exists(os.path.dirname(filename))
        f = file(filename, "w")
        f.write(data)
        f.close()

    def get_rules(self):
        return self.__get_rules()

    def copy_to(self, store_path):
        # publish all crap to static files
        for url in self.__get_urls():
            self.__save_page(url, store_path)

        #copy static files
        for f in PUBLISH_ADD_FILES:
            result = os.popen('cp -rv %s %s%s/' % (f, store_path, YEAR))
            for line in result.readlines():
                print "saving: %s" % line.strip("\n\r")


if __name__ == '__main__':
    app = create_app({
        'FACEBOOK_ID': '536796489696963',
        'FACEBOOK_SECRET': '1203f3bd7633d102e30cc02f7d61b3f8',
        'TWITTER_KEY': 'H3YBefguk72B38Yt5KdDg',
        'TWITTER_SECRET': 'cPmxDXCm3MgVPruiCjYXioZhUubLvehnTiVgI1M',
        'TESTING': True,
        'SECRET_KEY': 'jednadvehonzajde',
        'YEAR': YEAR,
        'ARCHIVE': True
    })
    publisher = Publisher(app)
    publisher.copy_to("./archive/")
