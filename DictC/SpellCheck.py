#!/usr/bin/env python
# -*- coding: utf-8 -*-
import enchant
from DictC.BaseDict import BaseDict


class SpellCheck(BaseDict):
    metadata = {
        'id': 'spellcheck',
        'name': u'拼写检查',
    }

    def __init__(self):
        super(SpellCheck, self).__init__()

    @staticmethod
    def fetchSuggestion(keyword):
        d = enchant.request_dict("en_US")
        return map(lambda w: (w, w), d.suggest(keyword))
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
