#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import struct
from ctypes import (
    CDLL,
    c_int,
    POINTER,
)
from BaseDict import BaseDict
from os import listdir
import os.path
from os.path import (
    expanduser,
    isdir,
    exists,
)


class StarDict(BaseDict):
    metadata = {
        'id': 'stardict',
        'name': u'星际译王'
    }

    dicts = {}

    _MAX_KEYWORD_LENGTH = 255
    _size = struct.calcsize('!ll')
    _clib = 'libstardict.so'

    def __init__(self):
        super(StarDict, self).__init__()

        libstardict = CDLL(self.getCLib())
        self.parse_idx = libstardict.parse_idx

        dicts = self.dicts
        basedirs = ["~/.stardict/dic", "/usr/share/stardict/dic"]
        dic_path = []
        for basedir in basedirs:
            expanded_basedir = expanduser(basedir)
            if not exists(expanded_basedir) or not isdir(expanded_basedir):
                continue
            _dic_path = listdir(expanded_basedir)
            _dic_path = map(
                lambda dirname: expanduser("%s/%s" % (basedir, dirname)),
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
            idxs = self._read_idx(dic_idx_data, ifo)
            dicts[basename]['idx'] = idxs
            dicts[basename]['idx_data'] = dic_idx_data

            dic_file = gzip.open("%s/%s.dict.dz" % (dic, basename), "rb")
            dicts[basename]['dict'] = dic_file

    @staticmethod
    def getCLib():
        dl_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(dl_dir, StarDict._clib)

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
        if ifo.get('sametypesequence') == "tm":
            type, detail = explain.split('\0')
            if type:
                explain = "[%s]\n%s" % (type, detail)
            else:
                explain = detail
        explain = '\t' + explain
        explain = explain.replace("\n", "\n\t")
        return "%s\n\n%s" % (ifo['bookname'], explain)

    def _read_ifo(self, ifo_filename):
        file = open(ifo_filename, "rb")
        lines = file.read().split("\n")
        ifo = {}
        for line in lines:
            if line.find('=') >= 0:
                key, val = line.split('=')
                ifo[key] = val
        return ifo

    def _read_idx(self, data, ifo):
        count = int(ifo['wordcount'])
        filesize = int(ifo['idxfilesize'])

        parse_idx = self.parse_idx
        parse_idx.restype = POINTER(c_int * count)
        contents = parse_idx(data, filesize, count, self._size).contents
        return tuple(contents)

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
        size = self._size
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
