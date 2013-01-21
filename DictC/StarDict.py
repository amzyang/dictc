#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import struct
import ConfigParser
from collections import deque
from BaseDict import BaseDict
from os import listdir
from os.path import (
    isfile,
    expanduser
)


class StarDict(BaseDict):
    metadata = {
        'id': 'stardict',
        'name': u'星际译王'
    }

    dicts = {}

    _MAX_KEYWORD_LENGTH = 255

    def __init__(self):
        super(StarDict, self).__init__()
        dicts = self.dicts
        basedirs = ["~/.stardict/dic", "/usr/share/stardict/dic"]
        dic_path = []
        for basedir in basedirs:
            _dic_path = listdir(expanduser(basedir))
            _dic_path = map(lambda dirname: expanduser("%s/%s" % (basedir,
                                                                 dirname)),
                           _dic_path)
            dic_path.extend(_dic_path)
        for dic in dic_path:
            filenames = listdir(dic)
            basename = False

            for filename in filenames:
                ridx = filename.rfind(".ifo")
                if ridx >= 0 and filename[ridx:] == ".ifo":
                    basename = filename[:ridx]
                    break
                if basename is False:
                    continue
            dicts[basename] = {}
            ifo = self._read_ifo("%s/%s.ifo" % (dic, basename))
            dicts[basename]['ifo'] = ifo
            dic_idx = open("%s/%s.idx" % (dic, basename), "rb")
            dic_idx_data = dic_idx.read()
            idxs = self._read_idx(dic_idx_data)
            dicts[basename]['idx'] = idxs
            dicts[basename]['idx_data'] = dic_idx_data

            dic_file = gzip.open("%s/%s.dict.dz" % (dic, basename), "rb")
            dicts[basename]['dict'] = dic_file

    def soundUri(self, keyword):
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
        file_func = lambda keyword, path: isfile("%s/%s/%s" % (path,
                                                               keyword[0],
                                                               keyword))
        audio = False
        for path in paths:
            part = file_func(path, keyword)
            if isfile("%s.wav" % part):
                audio = "%s.wav" % part
                break
            if isfile("%s.mp3" % part):
                audio = "%s.mp3" % part
                break
        return audio

    @staticmethod
    def getLink(keyword):
        return ""

    def getOutput(self):
        dic_outputs = []
        for dic in self.dicts.values():
            output = self.read_dic(dic)
            if output is not None:
                dic_outputs.append(output)
        nr = len(dic_outputs)
        if not nr:
            return False, ''
        else:
            output = "共找到 %d 条记录\n\n\n" % nr
            output += "\n\n\n".join(dic_outputs)
            return True, output

    def read_dic(self, dic):
        ifo = dic['ifo']
        idx = dic['idx']
        idx_data = dic['idx_data']
        dic_file = dic['dict']
        item = self._stardict_bin_find(idx, idx_data)
        if item is None:
            return None
        word, offset, size = item
        dic_file.seek(offset)
        explain = dic_file.read(size)
        if ifo['sametypesequence'] == "tm":
            type, detail = explain.split('\0')
            if type:
                explain = "[%s]\n%s" % (type, detail)
            else:
                explain = detail
        explain = '\t' + explain
        explain = explain.replace("\n", "\n\t")
        return "%s\n\n%s" % (ifo['bookname'], explain)
        return None

    def _read_ifo(self, ifo_filename):
        file = open(ifo_filename, "rb")
        lines = file.read().split("\n")
        ifo = {}
        for line in lines:
            if line.find('=') >= 0:
                key, val = line.split('=')
                ifo[key] = val
        return ifo

    def _read_idx(self, data):
        index_file_len = len(data)
        pos = 0
        size = struct.calcsize('!ll')
        idxs = deque()
        while pos < index_file_len:
            while data[pos] != '\0':
                pos += 1
            pos += size + 1
            idxs.append(pos)
        return idxs

    def _stardict_bin_find(self, idxs, data):
        low = 0
        high = len(idxs) - 1
        mid = (low + high) / 2

        while low <= high:
            if mid == 0:
                string = data[0:idxs[mid]]
            else:
                string = data[idxs[mid - 1]:idxs[mid]]
            word, offset, size = self._block_to_list(string)
            val = _stardict_strcmp(word, self.keyword)
            if val == 0:
                return word, offset, size
            elif val > 0:
                high = mid - 1
                mid = (low + high) / 2
            else:
                low = mid + 1
                mid = (low + high) / 2

        return None

    def _block_to_list(self, string):
        fmt = '!ll'
        size = struct.calcsize(fmt)
        sep = len(string) - size - 1
        word = string[0:sep]
        offset, size = struct.unpack(fmt, string[sep + 1:])
        return word, offset, size


def _stardict_strcmp(s1, s2):
    val = cmp(s1.lower(), s2.lower())
    if (val == 0):
        return cmp(s1, s2)
    else:
        return val
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
