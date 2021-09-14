# !/usr/bin/python
# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals

import sys
import logging

if "2.7" in str(sys.version):
    reload(sys)
    sys.setdefaultencoding('utf-8')

import argparse
import os
import re
import subprocess
import time
from py_src.args_paser import args_parser

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_root)

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a %d %b %Y %H:%M:%S')

class WERComputer(object):
    align_text_cmd = "/ssd3/exec/sunyq/kaldi/src/bin/align-text "
    score_per_utt_pl = "/ssd3/exec/sunyq/kaldi/egs/wsj/s5/utils/scoring/wer_per_utt_details.pl "
    wer_cmd = "/ssd3/exec/sunyq/kaldi/src/bin/compute-wer "

    def __init__(self, args, lang):
        self.lang = lang
        self.args = args
        self.ts_set_path = args.ts_set_path
        test_data_set_name = args.ts_set_path
        test_data_set_name = re.sub(r"([\s\S]*)(/)$", r"\1", test_data_set_name)
        test_data_set_name = os.path.split(test_data_set_name)[-1]
        if len(test_data_set_name) == 0:
            test_data_set_name = os.path.split(args.ts_set_path)[-2]
        self.asr_output_file = os.path.join(
            project_root, "exp", "{}_{}_wavs_asr.txt".format(test_data_set_name, args.type))
        self.gt_format_file = os.path.join(
            project_root, "exp", "{}_{}_wavs_gt.txt".format(test_data_set_name, args.type))
        self.wer_dump_file = os.path.join(
            project_root, "exp", "{}_{}_wer.txt".format(test_data_set_name, args.type))
        exp_root = os.path.join(project_root, "exp")
        if not os.path.exists(exp_root):
            os.makedirs(exp_root)

    def score_per_utt(self, ref_txt, hyp_txt):
        # 简单的封装一下kaldi api, 输入的ref_txt 和hyp_txt格式和kaldi中text格式, 可以方便分析哪些地方是插入/删除/替换错误
        # 使用示例 score_per_utt("/ssd3/exec/guoyf/s5_en_guo/data/testset_8k_hires/oppo-8k/text","/ssd3/exec/guoyf/s5_en_guo/data/testset_8k_hires/oppo-8k/output_a.txt","a.txt")
        cmd = self.align_text_cmd + "--special-symbol="'***'"  ark:%s  ark:%s  ark,t:-  | " % (ref_txt, hyp_txt)
        cmd += self.score_per_utt_pl + "--special-symbol="'***'" "
        logging.info("score_per_utt command={}".format(cmd))
        popen = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        datalist = []
        for line in popen.stdout.readlines():
            datalist.append(line.strip())
        return datalist

    def computer_diff(self, ref_txt, hyp_txt):
        cmd = self.wer_cmd + " --text --mode=present ark:%s ark:%s " % (ref_txt, hyp_txt)
        os.system(cmd)

    def text_format_back(self, text):
        if self.lang == "cn":
            # 会把英文单词保留下来
            text = re.sub(r"，|。|《|》|？|！|、|[,?!\(\)\-]+|…", r" ", text)
            text = re.sub(r"[\s]+", r"@", text.lower())
            text = re.sub(r"", r" ", text)
            text = re.sub(r"([a-z\@\']{1,1})( )([a-z\@\']{1,1})", r"\1\3", text)
            text = re.sub(r"([a-z\@\']{1,1})( )([a-z\@\']{1,1})", r"\1\3", text)
            text = re.sub(r"[\s]*@", r" ", text)
            text = re.sub(r"[ ]+", r" ", text)
            # seg_list = jieba.cut(text, cut_all=False)
            text = text.strip()
            return text
        return text

    def text_format(self, text):
        if self.lang == "cn":
            return self.text_format_back(text)
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"", r" ", text)
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        elif self.lang == "jp":
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"", r" ", text)
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        elif self.lang == "ko":
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"", r" ", text)
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        elif self.lang == "en":
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        elif self.lang == "ru":
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        elif self.lang == "hi":
            # 会把英文单词按char分割
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        else:
            text = re.sub(r"\.|«|»|，|。|《|》|？|！|、|[,?!\(\)\-\"\']+|…", r" ", text.lower())
            text = re.sub(r"[ ]+", r" ", text)
            text = text.strip()
        return text

    def wavfile_name(self):
        pass

    def dump_asr_pred_output(self):
        st = time.time()
        exe = "python {}".format(os.path.join(project_root, "test", "py_src", "test_wavs.py"))
        command = "{} -ip {} -p {} -type {} -wavs_path {} -lg {} -audio_enc_type {} -noitn {} -nopunc {}".format(
            exe, self.args.ip, self.args.port, self.args.type,
            os.path.join(self.ts_set_path, "audios"), self.args.lang, self.args.audio_enc_type,
            self.args.noitn, self.args.nopunc)
        logging.info("command={}".format(command))
        popen = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pred_data = []
        lines = popen.stdout.readlines()
        logging.info("len(lines)={}".format(len(lines)))
        for line in lines:
            key = line.split()[0].strip()
            key = os.path.split(key)[-1].strip()
            text = " ".join(line.split()[1:]).strip()
            text = self.text_format(text)
            pred_data.append([key, text])
        pred_data = sorted(pred_data, key=lambda x: x[0])
        with open(self.asr_output_file, "w") as f:
            for data in pred_data:
                line = data[0] + "\t" + data[1] + "\n"
                f.write(line)
        logging.info("succsss write asr out info to {} time use: {}".format(self.asr_output_file, time.time() - st))

    def dump_gt_format_output(self):
        gt_data = []
        gt_file = os.path.join(self.ts_set_path, "label.txt")
        assert os.path.exists(gt_file)
        with open(gt_file, "r") as f:
            for line in f:
                assert len(line.split("###")) >= 2
                [key, text] = line.split("###")
                key = key.strip()
                text = text.strip()
                text = self.text_format(text)
                gt_data.append([key, text])
        gt_data = sorted(gt_data, key=lambda x: x[0])
        with open(self.gt_format_file, "w") as f:
            for data in gt_data:
                line = data[0] + "\t" + data[1] + "\n"
                f.write(line)
        logging.info("succsss write text info to {}".format(self.gt_format_file))

    def get_wer_output(self):
        command = "{} --text --mode=present ark:{} ark:{}".format(
            self.wer_cmd, self.gt_format_file, self.asr_output_file)
        logging.info("get_wer_output command={}".format(command))
        popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wer_datalist = []
        for line in popen.stdout.readlines():
            logging.info(line.strip())
            wer_datalist.append(line.strip())
        return wer_datalist

    def dump_wer(self):
        datalist = self.score_per_utt(self.gt_format_file, self.asr_output_file)
        wer_datalist = self.get_wer_output()
        datalist = [self.wer_dump_file] + wer_datalist + datalist
        with open(self.wer_dump_file, "w") as f:
            for line in datalist:
                f.write(line.strip() + '\n')
        logging.info("succsss write wer to {}".format(self.wer_dump_file))


def main(args):
    wer_computer = WERComputer(args, args.lang)
    wer_computer.dump_gt_format_output()
    wer_computer.dump_asr_pred_output()
    wer_computer.dump_wer()


if __name__ == "__main__":
    args = args_parser()
    main(args)
