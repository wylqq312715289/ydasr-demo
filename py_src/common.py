# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
Copyright 2018 The YouDao Authors. All Rights Reserved.
             2020 NetEase, YouDao (author: Wang Yulong)
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================
"""

#reload(sys)
#sys.setdefaultencoding('utf8')

import os, re
import zhon
import zhon.hanzi
import string

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_root)

def full2half(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

def normalization(s, language):
    """
    归一化
    """
    #1. 首尾去除空格换行符标点
    s = s.strip().strip(string.punctuation).strip(zhon.hanzi.punctuation)
    #2. 句子中间标点归一化
    if language == "en":
        s = re.sub(r"[%s%s%s]+" % (re.escape(string.punctuation.replace("\'", "")), zhon.hanzi.punctuation, "．"), ",", s)
    else:
        s = re.sub(r"[\s%s%s%s]+" % (re.escape(string.punctuation),zhon.hanzi.punctuation, "．"), ",", s)
    return s

def depunctuate(s, language):
    #remove_punct_map = dict.fromkeys(map(ord, string.punctuation))
    #s = s.translate(remove_punct_map)
    s = full2half(s)
    if language == "en":
        s = re.sub(r"[%s%s%s]+" % (re.escape(string.punctuation.replace("\'", "")), zhon.hanzi.punctuation, "．"), " ", s)
        #stmp = s.strip()
        #s = ' '.join(stmp.split())
    else:
        s = re.sub(r"[\s%s%s%s]+" % (re.escape(string.punctuation), zhon.hanzi.punctuation, "．"), "", s)
    #fil = re.compile(u'[^0-9a-zA-Z\u4e00-\u9fa5\u0800-\u4e00\uac00-\ud7ff\']+', re.UNICODE)
    #fil = re.compile(u'[^0-9a-zA-Z\']+', re.UNICODE)
    #s = fil.sub(' ', s)
    #temp = s
    #temp = temp.replace("\'", "").replace(" ", "")
    #if not temp.isalnum():
    #    print(temp.encode('unicode_escape'))
    return s

