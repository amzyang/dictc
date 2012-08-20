#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TODO: replace raw_input by cmd module
# @TODO: 在键盘中断时关闭线程
import subprocess
import tempfile
import os
import sys
import readline
import threading
from DictC.BaseDict import BaseDict
from DictC.QQDict import QQDict
from DictC.DictCnDict import DictCnDict
from DictC.BingDict import BingDict as BingDict
import unicodedata
import argparse


def width(string):
    return sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in string)


class SoundThread(threading.Thread):
    def __init__(self, s):
        threading.Thread.__init__(self)
        self.s = s
        self._uri = ''

    def set_uri(self, uri):
        self._uri = uri
        self.s.do(self.uri)

    def get_uri(self):
        return self._uri

    def del_uri(self):
        del self._uri

    uri = property(get_uri, set_uri, del_uri, "Change src uri!")

    def run(self):
        pass


class FetchThread(threading.Thread):
    def __init__(self, keyword):
        threading.Thread.__init__(self)
        self.keyword = keyword

    def run(self):
        userdict = Dict()
        userdict.setKeyword(self.keyword)
        status, content = userdict.getOutput()
        link = Dict.getLink(self.keyword)
        if status:
            content += "\n\n%s" % link
            output(content)
        else:
            print u'无解释'
            print link


class Completer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.prefix = None
        self.caches = {}
        self.format_string = "%s  %s"

    def complete(self, prefix, index):
        if prefix in self.caches:
            try:
                w, t = self.caches[prefix][index]
                if not t.strip():
                    return w
                else:
                    return self.format_string % (w, t)
            except IndexError:
                return None
            except KeyError:
                return None
        if not prefix in self.caches or prefix != self.prefix:
            words = Sugg.fetchSuggestion(prefix)
            if not len(words):
                return None
            self.words = words
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [
                (w.encode('utf8'), t.encode('utf8')) for w, t in self.words if
                w.encode('utf8').lower().startswith(prefix.lower())
            ]
            widest = max([width(w.decode('utf8')) for w, t in
                          self.matching_words])
            self.matching_words = [
                ("%s%s" % (w, ' ' * (widest - width(w.decode('utf8')))), t) for
                w, t in self.matching_words]
            self.prefix = prefix
            self.caches[prefix] = self.matching_words
        try:
            w, t = self.matching_words[index]
            if not t.strip():
                return w
            else:
                return self.format_string % (w, t)
        except IndexError:
            return None

    def run(self, prefix, index):
        self.complete(prefix, index)


def paging(content, pager):
    f = tempfile.NamedTemporaryFile()
    f.write(content)
    f.flush()
    proc = subprocess.Popen("%s %s" % (pager, f.name), shell=True)
    proc.communicate()
    f.close()


def output(content):
    try:
        pager = os.environ.get('PAGER', 'more')
        paging(content, pager)
    except Exception:
        print content


def thread(keyword):
    f = FetchThread(keyword)
    f.setDaemon(True)
    f.start()
    f.join()


def main():
    histfile = "%s/dict_qq_history_py" % tempfile.gettempdir()
    if (os.path.exists(histfile)):
        readline.read_history_file(histfile)
    hasSound = not args.nosound
    if hasSound:
        try:
            from DictC.Sound import Sound  # @hack
            s = Sound()
            t = SoundThread(s)
            t.setDaemon(True)
            t.start()
        except ImportError:
            hasSound = False

    if not args.words:
        try:
            print 'Press <Ctrl-D> or <Ctrl-C> to exit!'
            completer = Completer()
            readline.set_completer(completer.complete)
            readline.set_completer_delims('')
            while True:
                line = raw_input('>> ')
                keyword = line.strip()
                if len(keyword):
                    if hasSound:
                        t.uri = BaseDict.soundUri(keyword)
                    thread(keyword)
        except (EOFError, KeyboardInterrupt, SystemExit):
            pass
    else:
        keyword = ' '.join(args.words)
        if hasSound:
            t.uri = BaseDict.soundUri(keyword)
        thread(keyword)

    readline.write_history_file(histfile)


if __name__ == "__main__":
    dict_services = (QQDict, BingDict)
    completion_services = (QQDict, BingDict, DictCnDict)

    class CLIAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            for service in self.services:
                if service.metadata['id'] == values:
                    return setattr(namespace, self.dest, service)

    description = u'一个简单的在线查询单词小工具！'
    epilog = u"""
    当前版本：0.1.1

    主要功能：

    - 支持多个在线词典服务
      qq    dict.qq.com
      bing  dict.bing.com.cn
    - 支持交互式模式下按<Tab>自动补全
      qq,bing,dictcn(dict.cn)
    - 发音支持
      需要 gstreamer 的 python 绑定，可以使用 yum/apt-get 安装。

    使用示例：

    $ %s hello
    直接查询 hello

    $ %s
    进入交互式模式，按 <CTRL-d> 退出！

    $ %s -d bing -c dictcn
    使用 dict.bing.com.cn 的在线翻译，dict.cn 来做查询时的自动补全！

    代码链接：

    https://github.com/grassofhust/dictc

    License:

    Beerware (If we meet some day, and you think
    this stuff is worth it, you can buy me a beer.)
    """ % (sys.argv[0], sys.argv[0], sys.argv[0])
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                     formatter_class=formatter_class)
    CLIAction.services = dict_services
    parser.add_argument('-d', nargs='?',
                        help=u'词典（默认：qq）：%s ' %
                        ','.join(map(lambda d: d.metadata['id'],
                                     CLIAction.services)),
                        metavar=u'dictionary',
                        dest='dict',
                        action=CLIAction,
                        default=CLIAction.services[0],
                        choices=map(lambda d: d.metadata['id'],
                                    CLIAction.services),
                        )
    CLIAction.services = completion_services
    parser.add_argument('-c', nargs='?',
                        help=u'自动补全（默认：qq）：%s ' %
                        ','.join(map(lambda d: d.metadata['id'],
                                     CLIAction.services)),
                        metavar=u'completion',
                        dest='sugg',
                        action=CLIAction,
                        default=CLIAction.services[0],
                        choices=map(lambda s: s.metadata['id'],
                                    CLIAction.services),
                        )
    parser.add_argument('--nosound', help=u'禁用发音（默认启用）', dest='nosound',
                        action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.1.1')
    parser.add_argument('words', metavar='keyword or sentence', type=str,
                        nargs='*')
    args = parser.parse_args()

    Dict = args.dict
    Sugg = args.sugg

    main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
