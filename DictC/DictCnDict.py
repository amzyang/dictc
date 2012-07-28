# -*- coding: utf-8 -*-
import httplib
try:
    import simplejson
except ImportError:
    import json as simplejson
from BaseDict import BaseDict
from urllib import urlencode
from urllib import unquote_plus
from urllib import quote


class DictCnDict(BaseDict):
    metadata = {
        'id': 'dictcn',
        'name': u'海词',
    }

    def __init__(self):
        BaseDict.__init__(self)

    @staticmethod
    def fetchSuggestion(keyword):
        keyword = keyword.strip()
        conn = httplib.HTTPConnection('dict.cn', timeout=2)
        headers = {
            'Referer': 'http://dict.cn/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0.1',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'dictsid=1;'
        }
        params = {
            'callback': '',
            'q': keyword,
            'dict': 'dict',
        }
        conn.request('GET',
                '/apis/suggestion.php?%s' % urlencode(params),
                body=None,
                headers=headers)
        r = conn.getresponse()
        if r.status == 200:
            completions = simplejson.loads(r.read())['s']
            base_dict = BaseDict()
            clean = lambda s: unquote_plus(s.strip())
            data = [(clean(item['g']), base_dict.html2txt(clean(item['e'])))
                    for item in completions]
        else:
            data = []
        conn.close()
        return data

    @staticmethod
    def getLink(keyword):
        return "http://dict.cn/%s" % quote(keyword)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
