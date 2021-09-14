# !/usr/bin/env python
# -*- coding: UTF-8 -*-
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
import argparse


class BaseParams(object):
    type = "stream"
    url = ""
    rate = 32000
    save_adaptation_state = ""
    send_adaptation_state = ""
    content_type = ""
    port = "8080"
    lang = "cn"
    rescore = "false"
    booked_words = "None"
    audio_enc_type = "wav"
    vad_head_sil = "36000000"
    vad_tail_sil = "36000000"
    opus_sample_rate = "16000"
    had_wav_header = "1"
    ip = "localhost"
    mode = "full"
    ts_set_path = ""
    w = ""
    time = 50
    samples = 2000
    pool = 50
    wavs_path = ""


def args_parser():
    parser = argparse.ArgumentParser(description='Command line client for kaldi gst server')
    parser.add_argument('-type', '--type', default="stream", dest="type",
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
    parser.add_argument('-rescore', '--rescore', default="true", dest="rescore", help="wither rescore")
    parser.add_argument('-booked_words', '--booked_words', default="None", dest="booked_words",
                        help="user booked words")
    parser.add_argument('-audio_enc_type', '--audio_enc_type', default="wav", dest="audio_enc_type",
                        help="audio_enc_type [wav,pcm,opus]")
    parser.add_argument('-vad_head_sil', '--vad_head_sil', default="3600000", dest="vad_head_sil",
                        help="vad_head_sil")
    parser.add_argument('-vad_tail_sil', '--vad_tail_sil', default="3600000", dest="vad_tail_sil",
                        help="vad_tail_sil")
    parser.add_argument('-opus_sample_rate', '--opus_sample_rate', default="16000", dest="opus_sample_rate",
                        help="opus_sample_rate")
    parser.add_argument('-had_wav_header', '--had_wav_header', default="1", dest="had_wav_header",
                        help="had_wav_header")
    parser.add_argument('-ip', '--ip', default="localhost", dest="ip", help="ip host")
    parser.add_argument('-mode', '--mode', default="full", dest="mode", help="stream output mode: full or clear.")
    parser.add_argument('-ts_set_path', '--ts_set_path', default="", dest="ts_set_path",
                        help="test set root path. must contain label.txt(file)、video(path)")
    parser.add_argument('-w', '--w', default="", dest="audiofile",
                        help="test set root path. must contain label.txt(file)、video(path)")
    # 持续请求的时长
    parser.add_argument('-time', '--time', default=50, dest="time", type=int)
    parser.add_argument('-speed', '--speed', dest="speed", default=1, type=int,
                        help="send wav speed when stream test. egs 1 2 3(speed up)")
    parser.add_argument('-n', '--samples', default=2000, dest="samples", type=int)
    parser.add_argument('-noitn', '--noitn', default=0, dest="noitn", type=int)
    parser.add_argument('-nopunc', '--nopunc', default=0, dest="nopunc", type=int)
    parser.add_argument('-pool', '--pool', default=50, dest="pool", type=int)
    parser.add_argument('-wavs_path', '--wavs_path', default="", dest="wavs_path",
                        help="Audio files to be sent to the server")
    args = parser.parse_args()
    return args
