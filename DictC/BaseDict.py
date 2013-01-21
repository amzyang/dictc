# -*- coding: utf-8 -*-
import ConfigParser
from os.path import (
    isfile,
    expanduser
)
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
    def soundUri(keyword, engine="youdao"):
        # gstatic = "https://www.gstatic.com/dictionary/static/sounds/de/0/"
        # return "%s%s.mp3" % (gstatic, keyword)
        def youdao(keyword):
            return "http://dict.youdao.com/dictvoice?%s" % urlencode({'audio':
                                                                  keyword})

        def google(keyword):
            gstatic = "https://www.gstatic.com/dictionary/static/sounds/de/0/"
            return "%s%s.mp3" % (gstatic, keyword)

        def local(keyword):
            # WyabdcRealPeopleTTS/a/ad.wav
            # OtdRealPeopleTTS/a/ad.wav
            cfg_path = expanduser("~/.stardict/stardict.cfg")
            if isfile(cfg_path):
                config = ConfigParser.ConfigParser()
                config.read(cfg_path)
                cfg_path = config.get("/apps/stardict/preferences/dictionary",
                                      "tts_path")
                cfg_path = expanduser(cfg_path)
            paths = ['~/.stardict/OtdRealPeopleTTS',
                        '~/.stardict/WyabdcRealPeopleTTS',
                        '/usr/share/WyabdcRealPeopleTTS',
                        '/usr/share/OtdRealPeopleTTS']
            paths = map(expanduser, paths)
            paths.remove(cfg_path)
            paths.insert(0, cfg_path)
            file_func = lambda keyword, path: expanduser("%s/%s/%s" % (path,
                                                                   keyword[0],
                                                                   keyword))
            audio = False
            for path in paths:
                part = file_func(keyword, path)
                if isfile("%s.wav" % part):
                    audio = "%s.wav" % part
                    break
                if isfile("%s.mp3" % part):
                    audio = "%s.mp3" % part
                    break
            if not audio:
                return False
            return "file:///%s" % audio

        uri = local(keyword)

        if not uri:
            uri = youdao(keyword)

        return uri

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
