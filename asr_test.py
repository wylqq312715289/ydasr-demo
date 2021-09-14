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
from py_src.ws_client import WSClient
import logging

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a %d %b %Y %H:%M:%S')

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_root)


def test_stream(args):
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
                  lang=args.lang, booked_words=args.booked_words, stream_mode=args.mode, byterate=args.rate,
                  save_adaptation_state_filename=args.save_adaptation_state,
                  send_adaptation_state_filename=args.send_adaptation_state, )
    ws.connect()
    result = ws.wait_wsclose()
    ws.close()


def test_onetime(args):
    # print(len(open(args.audiofile).read()))
    # b64_len = len(base64.b64encode(open(args.audiofile).read()))
    # print(b64_len)
    # exit()
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
    logging.info(d.read())


if __name__ == "__main__":
    args = args_parser()
    print(args.audiofile)
    if args.type == "onetime":
        test_onetime(args)
    elif args.type == "stream":
        test_stream(args)
    else:
        print("error type !!!")
