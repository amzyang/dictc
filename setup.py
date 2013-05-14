#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup


def extra_dependencies():
    import sys
    ret = []
    if sys.version_info < (2, 7):
        ret.append('argparse')
    return ret


setup(
    name='dictc',
    version='0.1.1',
    url='https://github.com/grassofhust/dictc',
    author='kikyo',
    author_email='frederick.zou@gmail.com',
    py_modules=[],
    packages=['DictC'],
    scripts=['dictc'],
    license='Beerware',
    data_files=[('/etc/bash_completion.d/',
                 ['scripts/dictc-bash-completion.sh']),
                ('/usr/share/zsh/site-functions/', ['scripts/_dictc'])],
    description=u'一个简单的在线查询单词小工具！',
    long_description=u"""主要功能：
    - 支持多个在线词典服务
    qq        dict.qq.com
    bing      dict.bing.com.cn
    stardict  星际译王
    - 支持交互式模式下按<Tab>自动补全
    qq/bing/dict(dict.cn)/spellcheck(拼写检查)/external(外部命令)
    - 发音支持
    需要 gstreamer 的 python 绑定，可以使用 yum/apt-get 安装。
    """,
    install_requires=extra_dependencies()
)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
