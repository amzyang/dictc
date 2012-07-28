# -*- coding: utf-8 -*-
from urllib import urlencode
from HTMLParser import HTMLParser
try:
    from django.utils.html import strip_tags
except ImportError:
    import re
    def strip_tags(text):
        return re.sub(r'<[^>]*?>', '', text)


class BaseDict(object):
    metadata = {
        'id': 'base',
        'name': u'词典基类',
    }

    def __init__(self):
        pass

    def setKeyword(self, keyword):
        self.keyword = keyword

    def getKeyword(self):
        return self.keyword

    @staticmethod
    def soundUri(keyword):
        return "http://dict.youdao.com/dictvoice?%s" % urlencode({'audio':
                                                                  keyword})

    @staticmethod
    def fetchSuggestion(keyword):
        """Fetching automatic suggestion

        We use dict.cn's by default.
        """
        keyword = keyword.strip()
        return [keyword]

    @staticmethod
    def getLink(keyword):
        return ""

    def html2txt(self, text):
        return strip_tags(BaseDict.html_entity_decode(text))

    @staticmethod
    def html_entity_decode(text):
        h = HTMLParser()
        return h.unescape(text)

    def getOutput(self):
        return False, ''


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
