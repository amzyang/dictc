#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import dictc


class DictCTest(unittest.TestCase):
    def setUp(self):
        pass


class BaseDictTest(unittest.TestCase):
    def setUp(self):
        from DictC.BaseDict import strip_tags
        self.strip_tags = strip_tags
        import re
        self.raw_strip_tags = lambda text: re.sub(r'<[^>]*?>', '', text)
        from DictC.BaseDict import BaseDict
        self.BaseDict = BaseDict

    def test_strip_tags(self):
        self.assertIsInstance(self.strip_tags.func_doc, str)
        self.assertEqual('hello', self.strip_tags('<>hello</>'))
        self.assertEqual('hello', self.strip_tags('<div>hello</div>'))

    def test_raw_strip_tags(self):
        self.assertIsNone(self.raw_strip_tags.func_doc)
        self.assertEqual('hello', self.raw_strip_tags('<>hello</>'))
        self.assertEqual('hello', self.raw_strip_tags('<div>hello</div>'))

    def test_fetchSuggestion(self):
        keyword = 'hello'
        self.assertEqual([keyword], self.BaseDict.fetchSuggestion(keyword))

    def test_set_get_keyword(self):
        keyword = 'hello'
        base_dict = self.BaseDict()
        base_dict.setKeyword(keyword)
        self.assertEqual(keyword, base_dict.getKeyword())

    def test_soundUri(self):
        pass

    def test_html2txt(self):
        pairs = [
            ('<b>Hello</b>', 'Hello'),
            ('&amp;', '&'),
            ('<b>&amp;</b>', '&')
        ]
        base_dict = self.BaseDict()
        for orig, raw in pairs:
            self.assertEqual(base_dict.html2txt(orig), raw)

    def test_getOutput(self):
        base_dict = self.BaseDict()
        self.assertTupleEqual((False, ''), base_dict.getOutput())

    def tearDown(self):
        # TODO: django is missing?
        import django.utils.html
        reload(django.utils.html)


class BingDictTest(unittest.TestCase):
    def setUp(self):
        self.keywords = ['addicted', 'hello', 'welcome', 'it\'s', '你',
                         'cancer']
        from DictC.BingDict import BingDict
        self.BingDict = BingDict
        self.bing = BingDict()

    def test_fetchSuggestion(self):
        keywords = [
            '你', "it's", 'hello'
        ]
        for keyword in keywords:
            data = self.BingDict.fetchSuggestion(keyword)
            self.assertTrue(data)

        self.assertEqual(10, len(data))
        self.assertTupleEqual(
            (u'hello', u'你好;您好;哈喽;喂,表示问候,打招呼或接电话时'),
            data[0]
        )

    def test_getOutput(self):
        for keyword in self.keywords:
            self.bing.setKeyword(keyword)
            status, content = self.bing.getOutput()
            self.assertTrue(status)


class DictCnTest(unittest.TestCase):
    def setUp(self):
        self.keywords = ['addicted', 'hello', 'welcome', 'it\'s', '你',
                         'cancer']
        from DictC.DictCnDict import DictCnDict
        self.DictCnDict = DictCnDict
        self.dict_cn = DictCnDict()

    def test_fetchSuggestion(self):
        keywords = [
            '你', "it's", 'hello'
        ]
        for keyword in keywords:
            data = self.DictCnDict.fetchSuggestion(keyword)
            self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
