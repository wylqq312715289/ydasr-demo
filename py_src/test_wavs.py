#!/usr/bin/python
# coding:utf-8
from __future__ import unicode_literals

import platform
import sys

if "2.7" in platform.python_version():
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import re
import base64
import urllib
import json
from multiprocessing.dummy import Pool as Pool
from args_paser import args_parser

from ws_client import WSClient

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_root)


def list_cut(x, batch_num):
    ans = [[] for i in range(batch_num)]
    for i, item in enumerate(x, 0):
        ans[i % batch_num].append(item)
    return ans


def test_stream(args, audiofiles):
    content_type = args.content_type
    if args.url == "":
        url = 'ws://%s:%s/asr' % (args.ip, args.port)
    else:
        url = args.url  # 方便测试线上服务
    result = []
    for audiofile in audiofiles:
        if content_type == '' and (re.findall(r".raw", audiofile)) > 0:
            content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, " \
                           "format=(string)S16LE, channels=(int)1" % (args.rate / 2)
        ws = WSClient(args=args, audiofile=audiofile,
                      url=url + '?%s' % (urllib.urlencode([("content-type", content_type)])),
                      lang=args.lang,
                      booked_words=args.booked_words,
                      stream_mode="pass",
                      byterate=args.rate,
                      save_adaptation_state_filename=args.save_adaptation_state,
                      send_adaptation_state_filename=args.send_adaptation_state, )
        try:
            ws.connect()
            ws.wait_wsclose()
            asr_out = parser_stream_asrout(ws.result)
            result.append([audiofile, asr_out])
        except:
            print("Connections is full")
    return result


def test_onetime(args, audiofiles):
    result = []
    options = "audio_enc_type=%s,had_wav_header=%s,opus_sample_rate=%s,muti_sentences=1,noitn=%d,nopunc=%d" % (
        args.audio_enc_type, args.had_wav_header, args.opus_sample_rate, args.noitn, args.nopunc)
    for audiofile in audiofiles:
        assert os.path.exists(audiofile)
        data = {'audio': base64.b64encode(open(audiofile).read()),
                'lang': args.lang,
                'options': options,
                'booked_words': args.booked_words,
                'timeout': 29}
        if args.url == "":
            url = 'http://%s:%s/asr' % (args.ip, args.port)
        else:
            url = args.url  # 方便测试线上服务
        d = urllib.urlopen(url=url, data=urllib.urlencode(data))
        res = parser_onetime_sentence(d.read())
        result.append([audiofile, res])
    return result


def parser_stream_asrout(asr_out):
    asr_text = ""
    for line in asr_out:
        json_data = json.loads(line.encode('utf-8'))
        text = json_data.get("text", '{}')
        sentence = ""
        text = json.loads(text.encode("utf-8"), encoding="utf-8")
        if len(text) == 0: continue
        for item in text:
            if item.get("partial") == False:
                sentence += item.get("sentence").encode("utf-8") + " "
        asr_text += sentence
    return asr_text


def parser_onetime_sentence(asr_out):
    json_data = json.loads(asr_out.encode('utf-8'))
    text = json_data.get("text", '{}')
    sentence = ""
    text = json.loads(text.encode("utf-8"), encoding="utf-8")
    if len(text) == 0: return ""
    for item in text:
        sentence += item.get("sentence").encode("utf-8")
    return sentence


def test(args):
    wav_files = os.listdir(args.wavs_path)
    wav_files = list(filter(lambda x: ".wav" in x or ".opus" in x, wav_files))
    wav_files = list(map(lambda x: os.path.join(args.wavs_path, x), wav_files))
    wav_files = sorted(wav_files, key=lambda x: x)
    if args.type == "onetime":
        result = test_onetime(args, wav_files)
    elif args.type == "stream":
        result = test_stream(args, wav_files)
    else:
        print("error type !!!")


def main(args):
    wav_files = os.listdir(args.wavs_path)
    wav_files = list(filter(lambda x: ".wav" in x or ".opus" in x, wav_files))
    wav_files = list(map(lambda x: os.path.join(args.wavs_path, x), wav_files))
    wav_files = sorted(wav_files, key=lambda x: x)
    wav_file_sets = list_cut(wav_files, args.pool)
    pool = Pool(processes=args.pool)
    thread_result = []
    for wav_files in wav_file_sets:
        if args.type == "onetime":
            res = pool.apply_async(test_onetime, (args, wav_files,))
            thread_result.append(res)
        elif args.type == "stream":
            res = pool.apply_async(test_stream, (args, wav_files,))
            thread_result.append(res)
        else:
            print("error type !!!")
    pool.close()
    pool.join()
    all_result = []
    for res in thread_result:
        for [audio_file, text] in res.get():
            all_result.append([audio_file, text])
    all_result = sorted(all_result, key=lambda x: x[1])
    for item in all_result:
        print(item[0] + "\t" + item[1])


if __name__ == "__main__":
    args = args_parser()
    main(args)
    # test(args)
