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
            paths = ['~/.stardict/OtdRealPeopleTTS',
                        '~/.stardict/WyabdcRealPeopleTTS',
                        '~/.stardict/voice',
                        '/usr/share/WyabdcRealPeopleTTS',
                        '/usr/share/OtdRealPeopleTTS',
                        '/usr/share/voice']
            paths = map(expanduser, paths)
            cfg_path = expanduser("~/.stardict/stardict.cfg")
            if isfile(cfg_path):
                config = ConfigParser.ConfigParser()
                config.read(cfg_path)
                tts_path = None
                try:
                    tts_path = config.get(
                        "/apps/stardict/preferences/dictionary", "tts_path")
                    tts_path = expanduser(tts_path)
                    paths.remove(tts_path)
                finally:
                    if tts_path:
                        paths.insert(0, tts_path)

            get_filename_without_extension = lambda keyword, path: expanduser(
                "%s/%s/%s" % (path, keyword[0], keyword))
            audio = False
            for path in paths:
                base = get_filename_without_extension(keyword, path)
                if isfile("%s.mp3" % base):
                    audio = "%s.mp3" % base
                    break
                if isfile("%s.wav" % base):
                    audio = "%s.wav" % base
                    break
            if not audio:
                return False
            return "file://%s" % audio

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
