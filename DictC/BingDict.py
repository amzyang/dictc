# -*- coding: utf-8 -*-
try:
    import simplejson
except ImportError:
    import json as simplejson
from BaseDict import BaseDict
import httplib
import re
from urllib import urlencode
from urllib import unquote_plus
from urllib import quote
from HTMLParser import HTMLParser
try:
    from django.utils.html import strip_tags
except ImportError:
    def strip_tags(text):
        return re.sub(r'<[^>]*?>', '', text)


class BingDict(BaseDict):
    metadata = {
        'id': 'bing',
        'name': u'Bing 词典',
    }

    def __init__(self):
        BaseDict.__init__(self)

    @staticmethod
    def fetchSuggestion(keyword):
        keyword = keyword.strip()
        conn = httplib.HTTPConnection('dict.bing.com.cn', timeout=2)
        headers = {'Referer': 'http://dict.bing.com.cn/?FORM=BNGCN',
                   'Host': 'dict.bing.com.cn',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        params = urlencode({'q': keyword, 't': 'sug', 'tlang': 'EN-US',
                            'ulang': 'ZH-CN', 'ut': 6})
        conn.request('POST',
                     '/io.aspx',
                     params,
                     headers=headers)
        r = conn.getresponse()
        if r.status == 200:
            data = simplejson.loads(r.read())
            # {#*HE*$}
            replace = lambda s: re.sub(r'{#\*(.+)\*\$}', r'\1', s)
            clean = lambda s: unquote_plus(s.strip())
            if not 'ACS' in data or not 'AC' in data['ACS']:
                return []
            completions = data['ACS']['AC']
            if not isinstance(completions, list):
                completions = [completions]

            clean_data = [(replace(clean(item['$'])),
                           clean(item.get('$I', ''))) for item in
                          completions]
            return clean_data
        else:
            data = []
        conn.close()
        return data

    @staticmethod
    def getLink(keyword):
        return "http://dict.bing.com.cn/#%s" % quote(keyword)

    def getOutput(self):
        try:
            self._fetch_content()
        except:
            raise
        if not self.data:
            return False, ''
        lines = []
        lines.extend(self._title())
        lines.extend(self._infs())
        lines.extend(self._def())
        lines.extend(self._sents())
        lines.extend(self._colls())
        lines.extend(self._phrases())
        lines.extend(self._thes())
        lines.extend(self._suggs())
        return True, '\n'.join(lines).encode('utf8')

    def _fetch_content(self):
        conn = httplib.HTTPConnection('dict.bing.com.cn', timeout=5)
        headers = {'Referer': 'http://dict.bing.com.cn/?FORM=BNGCN',
                   'Host': 'dict.bing.com.cn',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        params = urlencode({'q': self.keyword, 't': 'dict', 'tlang':
                            'EN-US',
                            'ulang': 'ZH-CN', 'ut': 'default'})
        conn.request('POST',
                     '/io.aspx',
                     params,
                     headers=headers)
        r = conn.getresponse()
        if r.status == 200:
            data = simplejson.loads(r.read())
        else:
            data = False
        conn.close()
        if 'ROOT' in data:
            self.data = data['ROOT']
        else:
            self.data = None

    def html2txt(self, text):
        h = HTMLParser()
        text = h.unescape(text)
        return strip_tags(unquote_plus(text))

    def keywordSoundUri(self):
        prefix = "http://media.engkoo.com:8129/en-us/"
        if 'AH' in self.data and '$' in self.data['AH']:
            hash = self.data['AH']['$'].strip()
            if len(hash) == 0:
                return None
            return "%s%s.mp3" % (prefix, hash)
        else:
            return None
        return None

    def _colls(self):
        """搭配
        adv.+v.
        warmly welcome

        adj.+n.
        welcome news
        welcome change
        welcome guest
        welcome mat
        welcome relief

        v.+n.
        welcome sight
        get welcome
        welcome proposal
        """
        lines = []
        if 'COLLS' in self.data and self.data['COLLS']:
            colls = self.data['COLLS']
            if 'CS' in colls:
                lines.append(u'\n搭配')
                if isinstance(colls['CS'], list):
                    cs = colls['CS']
                else:
                    cs = [colls['CS']]
                for parts in cs:
                    lines.append('\n\t%s' % parts['$REL'])
                    if 'C' in parts:
                        if isinstance(parts['C'], list):
                            for words in parts['C']:
                                lines.append('\t%s' %
                                             ' '.join(filter(lambda x: x,
                                                             words.values())))
                        else:
                            lines.append('\t%s' %
                                         ' '.join(filter(lambda x: x,
                                                         parts['C'].values())))
                return lines
            else:
                return lines
        else:
            return lines

    def _def(self):
        """解释
        adj.  1.  很好的;可喜的,叫人快乐的,可感谢的
              2.  受欢迎的,吃香的
              3.  可随便使用,能自由使用;不必感谢的;〈谑〉随便...罢

        int.  1.  欢迎

        n.    1.  欢迎,款待;欢迎辞
              2.  自由使用[享受]的特权

        v.    1.  欢迎

              网络释义:

              1.  不客气
                    http://www.crazyenglish.com/thread-5849-3-1.html
              2.  日期
                    http://learning.sohu.com/lan/ying/8033.htm
        """
        if not 'DEF' in self.data:
            return []
        maximums = [0]
        sens = []
        lines = [u'\n解释']
        for item in self.data['DEF']:
            if not 'SENS' in item:
                continue
            if isinstance(item['SENS'], list) and item['SENS']:
                maximums.append(max([len(sen['$POS']) for sen in
                                     item['SENS']]))
                sens.extend(item['SENS'])
            else:
                maximums.append(len(item['SENS']['$POS']))
                sens.append(item['SENS'])
        widest = max(maximums)
        for idx, sen in enumerate(sens):
            if isinstance(sen['SEN'], list):
                explains = [s['D']['$'] for s in sen['SEN']]
            else:
                explains = [sen['SEN']['D']['$']]
            lines.append("\t%s" % sen['$POS'])
            lines.extend(["\t%s  %s" % (" " * widest, unquote_plus(explain))
                          for explain in explains])

        return lines

    def _infs(self):
        """
        词形变化   welcomes   welcoming   welcomed
        """
        lines = []
        if not 'INFS' in self.data or not 'INF' in self.data['INFS']:
            return lines

        inf = self.data['INFS']['INF']
        if not isinstance(inf, list):
            inf = [inf]
        words = list(set([i['I-E']['$'] for i in inf]))
        lines.append('%s  %s' % (u'词形变化', '  '.join(words)))
        return lines

    def _phrases(self):
        """
        短语
        """
        if not 'PHRASES' in self.data:
            return []
        if not 'PH' in self.data['PHRASES']:
            return []
        ph = self.data['PHRASES']['PH']
        if not isinstance(ph, list):
            ph = [ph]
        if not ph:  # empty list
            return []
        widest = max([len(pair['$T'].strip()) for pair in ph])
        lines = [u'\n短语']
        for pair in ph:
            lines.append("\t%s  %s" % (pair['$T'].ljust(widest, ' '),
                                       pair['$']))
        return lines

    def _title(self):
        """
        good  US: [ɡʊd]
        """
        if 'PROS' in self.data and 'PRO' in self.data['PROS']:
            if isinstance(self.data['PROS']['PRO'], dict):
                return ["%s  %s [%s]" % (self.data['$INPUT'],
                                       self.data['PROS']['PRO']['$L'],
                                       self.data['PROS']['PRO']['$'])]
            else:
                pros = ["%s [%s]" % (pro['$L'], pro['$']) for pro in
                        self.data['PROS']['PRO']]
                return ["%s %s" % (self.data['$INPUT'], ' '.join(pros))]
        return [self.data['$INPUT']]

    def _sents(self):
        """
        "It is such a joy to welcome the Miami Heat to the White House," Bush
            told a packed crowd in the East Room. [点击朗读] [点击观看视频]
        这是热火队的第一个NBA总冠军。
        www.chinadaily.com.cn/language_tips/2007-02/28/content_816094.htm

        To be clear, a strong Europe is always welcome by Beijing for
            geopolitical reasons. [点击朗读] [点击观看视频]
        要清楚,出于地缘政治方面的原因,一个强大的欧洲总是会受到中国政府的欢迎。
        http://www.ftchinese.com/story/001041490
        """
        # @TODO: sound support
        if not 'SENTS' in self.data or not 'SEN' in self.data['SENTS']:
            return []
        sen = self.data['SENTS']['SEN']
        lines = [u'\n例句']
        for sent in sen:
            lines.append("\n\t%s" % self._clean(sent['EN']['D']['$']))
            lines.append("\t%s" % self._clean(sent['CN']['D']['$']))
            lines.append("\t%s" % self.html2txt(sent['EN']['S']['$']))
        return lines

    def _clean(self, text):
        _text = re.sub(r'{([1-9][0-9]*)#(.*?)\$\1}', r'\2', text)
        _text = re.sub(r'{##?\*(.*?)\*\$\$?}', r'\1', _text)
        return self.html2txt(_text)

    def _suggs(self):
        """
        您要找的是不是

        goods
        gd
        gd.
        G.D.
        God
        """
        # @TODO sound support
        if not 'SUGGS' in self.data:
            return []
        if not 'PH' in self.data['SUGGS']:
            return []
        suggs = self.data['SUGGS']['PH']['I']
        lines = [u'\n推荐']
        if not isinstance(suggs, list):
            suggs = [suggs]
        for item in suggs:
            lines.append("\t%s" % item['$'])
            lines.append("\t%s\n" % item['$DEF'])
        return lines

    def _thes(self):
        """
        同义词

            v.
            greet
            receive
            accept
            appreciate
            (反义词) snub
            (反义词) reject

            adj.
            at home
            pleasurable
            longed-for
            long-awaited
            (反义词) unwelcome
            (反义词) untimely

            n.
            greeting
            reception
            salutation
            red carpet
            hospitality
            (反义词) farewell
        """
        if not 'THES' in self.data:
            return []
        if not 'THE' in self.data['THES']:
            return []
        the = self.data['THES']['THE']
        if not isinstance(the, list):
            the = [the]

        lines = [u'\n同反义词']
        for part in the:
            if isinstance(part, list):
                for innerpart in part:
                    lines.append("\n\t%s" % innerpart['$POS'])
                    for cat in ['S', 'A']:
                        if cat in innerpart:
                            items = innerpart[cat]
                            if not isinstance(items, list):
                                items = [items]
                            if cat == 'A':
                                lines.extend([u"\t\t(反义词) %s" % item['$'] for
                                              item in items])
                            else:
                                lines.extend(["\t\t%\s" % item['$'] for item in
                                              items])
            else:
                lines.append("\n\t%s" % part['$POS'])
                for cat in ['S', 'A']:
                    if cat in part:
                        items = part[cat]
                        if not isinstance(items, list):
                            items = [items]
                        if cat == 'A':
                            lines.extend([u"\t\t(反义词) %s" % item['$'] for
                                          item in items])
                        else:
                            lines.extend(["\t\t%s" % item['$'] for item in
                                          items])
        return lines


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
