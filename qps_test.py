#!/usr/bin/python
# coding:utf-8
import sys

if "2.7" in str(sys.version):
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import re
import base64
import urllib
from py_src.args_paser import args_parser
from py_src.test_wavs import parser_stream_asrout
from py_src.ws_client import WSClient
from multiprocessing.dummy import Pool as Pool
import logging
import time
import json

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a %d %b %Y %H:%M:%S')

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_root)


def test_stream(args):
    st = time.time()
    content_type = args.content_type
    if args.url == "":
        url = 'ws://%s:%s/asr' % (args.ip, args.port)
    else:
        url = args.url  # 方便测试线上服务
    if content_type == '' and (re.findall(r".raw", args.audiofile)) > 0:
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, " \
                       "format=(string)S16LE, channels=(int)1" % (args.rate / 2)
    ws = WSClient(args=args, audiofile=args.audiofile,
                  url=url + '?%s' % (urllib.urlencode([("content-type", content_type)])),
                  lang=args.lang, booked_words=args.booked_words, stream_mode="pass", byterate=args.rate,
                  save_adaptation_state_filename=args.save_adaptation_state,
                  send_adaptation_state_filename=args.send_adaptation_state, )
    ws.connect()
    result = ws.get_full_hyp()
    ws.close()
    result = parser_stream_asrout(ws.result)
    time_use = float(time.time() - st)
    return [time_use, result.encode('utf-8')]

def test_onetime(args):
    st = time()
    options = "audio_enc_type=%s,had_wav_header=%s,opus_sample_rate=%s,muti_sentences=false" % (
        args.audio_enc_type, args.had_wav_header, args.opus_sample_rate,)
    data = {'audio': base64.b64encode(open(args.audiofile).read()),
            'lang': args.lang,
            'booked_words': args.booked_words,
            'options': options,
            'timeout': 29}
    if args.url == "":
        url = 'http://%s:%s/asr' % (args.ip, args.port)
    else:
        url = args.url  # 方便测试线上服务
    d = urllib.urlopen(url=url, data=urllib.urlencode(data))
    time_use = float(time.time() - st)
    res = d.read()
    res = json.loads(res)
    return [time_use, res]

def process_handel(args):
    if args.type == "stream":
        return test_stream(args)
    else:
        return test_onetime(args)

def mutithread_test():
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
    print(all_results[0])

def test1case():
    args = args_parser()
    print(args.audiofile)
    if args.type == "onetime":
        test_onetime(args)
    elif args.type == "stream":
        test_stream(args)
    else:
        print("error type !!!")

if __name__ == "__main__":
    #test1case()
    mutithread_test()