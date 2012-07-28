# -*- coding: utf-8 -*-
try:
    import simplejson
except ImportError:
    import json as simplejson
from BaseDict import BaseDict
import httplib
from urllib import urlencode
from urllib import quote


class QQDict(BaseDict):
    metadata = {
        'id': 'qq',
        'name': u'QQ 词典',
    }

    def __init__(self):
        BaseDict.__init__(self)

    @staticmethod
    def fetchSuggestion(keyword):
        keyword = keyword.strip()
        conn = httplib.HTTPConnection('dict.qq.com', timeout=2)
        headers = {'Referer': 'http://dict.qq.com/'}
        conn.request('GET',
                '/sug?%s' % (urlencode({'q': keyword}).split('=')[1]),
                body=None,
                headers=headers)
        r = conn.getresponse()
        if r.status == 200:
            data = r.read().decode('gb18030')
            clean = lambda s: s.strip()
            data = [tuple(map(clean, sug.split('\t'))) for sug in
                    data.split('\n') if sug]
        else:
            data = []
        conn.close()
        return data

    @staticmethod
    def getLink(keyword):
        return "http://dict.qq.com/dict?f=cloudmore&q=%s" % quote(keyword)

    def getOutput(self):
        try:
            self._fetch_content()
        except:
            raise

        if 'local' in self.data:
            local = self.data['local']
            lines = []
            for base in local:
                lines.extend(self._process_base(base))
                lines.extend(self._process_mor(base))
                lines.extend(self._process_des(base))
                lines.extend(self._process_sen(base))
                lines.extend(self._process_ph(base))

            if 'dlg' in self.data:
                dlg = self.data['dlg']
                lines.extend(self._process_dlg(dlg))

            if 'netsen' in self.data:
                netsen = self.data['netsen']
                lines.extend(self._process_netsen(netsen))

            return True, '\n'.join(lines).encode('utf8')
        else:
            return False, ''

    def _fetch_content(self):
        conn = httplib.HTTPConnection('dict.qq.com', timeout=5)
        headers = {'Referer': 'http://dict.qq.com/'}
        conn.request('GET',
                '/dict?%s' % urlencode({'f': 'web', 'q': self.keyword}),
                body=None,
                headers=headers)
        r = conn.getresponse()
        if r.status == 200:
            data = simplejson.loads(r.read())
        else:
            data = False
        conn.close()
        self.data = data

    def _process_base(self, base):
        """所查单词与读音

        look[luk]
        """
        if 'pho' in base:
            return ['\n%s [%s]' % (BaseDict.html_entity_decode(base['word']),
                                   BaseDict.html_entity_decode(','.join(base['pho'])))]
        else:
            return ['\n%s' % BaseDict.html_entity_decode(base['word'])]

    def _process_mor(self, base):
        """词形

        第三人称单数: looks动词过去式: looked过去分词: looked现在分词: looking
        """
        lines = []
        if 'mor' in base:
            lines.append('')
            pieces = []
            for mor in base['mor']:
                pieces.extend([v for k, v in mor.iteritems()])
            lines.append(' '.join(pieces))
        return lines

    def _process_des(self, base):
        lines = []
        if 'des' in base:
            lines.append('')
            for exp in base['des']:
                if isinstance(exp, basestring):
                    lines.append(exp)
                    continue
                s = []
                if 'p' in exp:
                    s.append(BaseDict.html_entity_decode(exp['p']))
                if 'd' in exp:
                    s.append(BaseDict.html_entity_decode(exp['d']))
                lines.append(' '.join(s))
        return lines

    def _process_ph(self, base):
        """词组
        look back 回顾
        look in 看望
        """
        lines = []
        if 'ph' in base:
            lines.append(u'\n\n词组')
            ph = base['ph']
            length = self._lengest(ph) + 3
            for word in ph:
                w = []
                if 'phs' in word:
                    w.append(self.html2txt(word['phs'].strip().ljust(length,
                                                                     ' ')))
                if 'phd' in word:
                    w.append(self.html2txt(word['phd'].strip()))
                lines.append("\t%s" % ''.join(w))

        return lines

    def _lengest(self, ph):
        return max([len(word['phs'].strip()) for word in ph if 'phs' in word])

    def _process_sen(self, base):
        """例句
        """
        lines = []
        if 'sen' in base:
            lines.append(u'\n\n例句')
            for sen in base['sen']:
                if 'p' in sen:
                    lines.append("\t" + sen['p'])
                else:
                    lines.append('')

                if 's' in sen:
                    for item in sen['s']:
                        lines.append("\t\t%s" % self.html2txt(item['es']))
                        lines.append("\t\t%s" % self.html2txt(item['cs']))
        return lines

    def _process_dlg(self, dlg):
        """情景对话
        """
        lines = [u'\n\n情景对话']
        for sense in dlg:
            lines.append("\n\t%s%s\n" % (self.html2txt(sense['t']),
                self.html2txt(sense['s'])))
            conversions = sense['c']
            for c in conversions:
                lines.append("\t\t%s: %s" % (self.html2txt(c['n']),
                                             self.html2txt(c['es'])))
                lines.append("\t\t   %s" % self.html2txt(c['cs']))
                lines.append('\n')

        return lines

    def _process_netsen(self, netsen):
        """网络例句
        """
        lines = [u'\n\n网络例句']
        for sense in netsen:
            lines.append("\n\t%s" % self.html2txt(sense['es']))
            lines.append("\t%s" % self.html2txt(sense['cs']))

        return lines

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
