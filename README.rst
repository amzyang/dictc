==============================================
dictc 简单的在线查询单词小工具！
==============================================

.. role:: raw-html(raw)
   :format: html

.. role:: key

当前版本：0.1.1

主要功能
---------

- 支持多个在线词典服务及星际译王词典
  `bing 词典 <http://dict.bing.com.cn>`_
  `stardict 词典 <http://www.stardict.org>`_

- 支持交互模式下按 :key:`Tab` 自动补全单词，支持在 bash/zsh 命令行下用 :key:`Tab` 补全参数及选项
- 发音支持

  需要 gstreamer 的 python 绑定，可以使用 yum/apt-get 安装。

安装方法
---------

环境依赖：
^^^^^^^^^^

* python 2.7 + linux
* gstreamer 的 python 绑定:

fedora 等安装方法： ::

    su -c 'yum -y install gstreamer-python'

ubuntu 等安装方法： ::

 su -c 'apt-get install python-gst0.10'

安装完依赖之后，接下来安装 dictc。

* 用源代码安装： ::

    git clone https://github.com/grassofhust/dictc.git
    cd dictc
    python setup.py install

* 下载 rpm 包安装

https://github.com/grassofhust/dictc/raw/master/assets/dictc-lastest.noarch.rpm

用法
-----

``dictc [-h] [-d dictionary] [-c completion] [--nosound] [-v] [keyword or sentence [keyword or sentence ...]]``

可选参数
^^^^^^^^^
::

     -h, --help           显示帮助信息
     -d dictionary        词典（默认：bing）：bing,stardict
     -c completion        自动补全（默认：bing）：bing,dictcn,spellcheck,external
     --nosound            禁用发音（默认：启用）
     -v, --version        显示版本信息

使用示例
-----------

``dictc hello``

直接查询 hello

``dictc``

进入交互式模式，按 :key:`CTRL-d` 退出！

``dictc -d bing -c dictcn``

使用 ``dict.bing.com.cn`` 的在线翻译， ``dict.cn`` 来做查询时的自动补全！

截图
-----

.. image:: https://raw.github.com/grassofhust/dictc/master/assets/screenshot.jpeg

待办项
--------

* 利用 ncurses 来输出，更好的控制输出样式及交互
* 后台查找
* 国际化
* 支持 stardict 词典格式？
* 使用本地真人语音库？
* python enchant, spell check support????

相关链接
----------

https://github.com/grassofhust/dictc

License
----------

Beerware (If we meet some day, and you think this stuff is worth it, you can buy me a beer.)

