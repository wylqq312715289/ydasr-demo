#!/usr/bin/python
# coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import argparse
import os
import re
import base64
import urllib

from py_src.ws_client import WSClient

script_root = os.path.dirname(os.path.abspath(__file__))


def args_parser():
    parser = argparse.ArgumentParser(description='Command line client for kaldi gst server')
    parser.add_argument('-type', '--type', default="onetime", dest="type",
                        help="test type onetime, stream, qus")
    parser.add_argument('-url', '--url', default="", dest="url", help="Server websocket url")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int, help="16k, 8k, 32k.")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='',
                        help="Use the specified content type (empty by default, for raw files the default is "
                             " audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, "
                             "format=(string)S16LE, channels=(int)1")
    parser.add_argument('-p', '--port', default="9096", dest="port", help="Server websocket port")
    parser.add_argument('-lg', '--lang', default="cn", dest="lang", help="test lang")
    parser.add_argument('-ip', '--ip', default="localhost", dest="ip", help="ip host")
    parser.add_argument('-mode', '--mode', default="full", dest="mode", help="stream output mode: full or clear.")
    parser.add_argument('audiofile', help="Audio file to be sent to the server", type=str)
    args = parser.parse_args()
    return args


def test_stream(args):
    content_type = args.content_type
    if args.url == "":
        url = 'ws://%s:%s/asr' % (args.ip, args.port)
    else:
        url = args.url  # 方便测试线上服务
    if content_type == '' and len(re.findall(r".raw", args.audiofile)) > 0:
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, " \
                       "format=(string)S16LE, channels=(int)1" % (args.rate / 2)
    ws = WSClient(audiofile=args.audiofile,
                  url=url + '?%s' % (urllib.urlencode([("content-type", content_type)])),
                  lang=args.lang, stream_mode=args.mode, byterate=args.rate,
                  save_adaptation_state_filename=args.save_adaptation_state,
                  send_adaptation_state_filename=args.send_adaptation_state, )
    ws.connect()
    result = ws.get_full_hyp()


def test_onetime(args):
    data = {'audio': base64.b64encode(open(args.audiofile).read()),
            'lang': args.lang, 'timeout': 29}
    if args.url == "":
        url = 'http://%s:%s/asr' % (args.ip, args.port)
    else:
        url = args.url  # 方便测试线上服务
    d = urllib.urlopen(url=url, data=urllib.urlencode(data))
    print(d.read())


if __name__ == "__main__":
    args = args_parser()
    if args.type == "onetime":
        test_onetime(args)
    elif args.type == "stream":
        test_stream(args)
    else:
        print("error type !!!")
