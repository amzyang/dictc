# -*- coding: utf-8 -*-
from BaseDict import BaseDict
import subprocess


class External(BaseDict):
    metadata = {
        'id': 'external',
        'name': u'外部命令',
    }

    def __init__(self):
        super(External, self).__init__()

    @staticmethod
    def fetchSuggestion(keyword, command="look"):
        if not keyword:
            return []
        output = subprocess.check_output([command, keyword])
        words = output.split("\n")
        words = filter(bool, words)
        return map(lambda word: (word, word), words)

    @staticmethod
    def getLink(keyword):
        return None


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
