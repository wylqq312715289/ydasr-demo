#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 5:35 PM
# @Author  : 王清尘
# @Site    : 
# @File    : test_qps
# @Software: PyCharm
# @describe:
from __future__ import unicode_literals

import base64
# import matplotlib.pyplot as plt
import json
import re
import sys
import time
import urllib
from multiprocessing.dummy import Pool as Pool

from py_src.args_paser import args_parser
from py_src.test_wavs import parser_stream_asrout
from py_src.ws_client import WSClient

reload(sys)
sys.setdefaultencoding('utf8')


def onetime_test(args):
    st = time.time()
    data = {
        'audio': base64.b64encode(open(args.audiofile).read()),
        'lang': args.lang,
        'timeout': 29
    }
    if args.url:
        url = args.url
    else:
        url = 'http://%s:%s/asr' % (args.ip, args.port)
    d = urllib.urlopen(url=url, data=urllib.urlencode(data))
    time_use = float(time.time() - st)
    res = d.read()
    res = json.loads(res)
    return [time_use, res]


def stream_test(args):
    st = time.time()
    content_type = args.content_type
    if content_type == '' and len(re.findall(r"\.raw$", args.audiofile)) > 0:
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" % (
                args.rate / 2)
    url = args.url if args.url != "" else "ws://%s:%s" % (args.ip, args.port)
    url = url + '?%s' % (urllib.urlencode([("content-type", content_type)]))
    wsclient = WSClient(args=args, audiofile=args.audiofile, url=url,
                        byterate=args.rate, lang=args.lang, stream_mode="pass",
                        save_adaptation_state_filename=args.save_adaptation_state,
                        send_adaptation_state_filename=args.send_adaptation_state)
    wsclient.connect()
    result = wsclient.wait_wsclose()
    wsclient.close()
    result = parser_stream_asrout(wsclient.result)
    time_use = float(time.time() - st)
    return [time_use, result.encode('utf-8')]


def process_handel(args):
    if args.type == "stream":
        return stream_test(args)
    else:
        return onetime_test(args)

if __name__ == '__main__':
    args = args_parser()
    st = time.time()
    print("Begin to work ...")
    pool = Pool(processes=args.pool)
    result = []
    while (True):
        if (time.time() - st >= args.time): break
        res = pool.apply_async(process_handel, (args,))  # 非阻塞
        result.append(res)
        if len(result) >= args.samples: break
    print("waiting join ..., sample=", len(result))
    pool.close()
    pool.join()
    print("pool_size = %d  sample_num = %d,  all Time USE: %.2fs, QPS=%f" % (
        args.pool, len(result), time.time() - st, 1.0 * len(result) / (time.time() - st)))
    all_results = list(map(lambda x: x.get(), result))
    all_results = sorted(all_results, key=lambda x: [0], reverse=True)
    # with open("qps_res.txt", "w") as f:
    #     for res in all_results:
    #         f.write(res[1] + "\n")
    print(all_results[0])
