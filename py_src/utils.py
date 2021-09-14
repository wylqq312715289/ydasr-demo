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

import h5py
import json
import os
import shutil
from datetime import datetime
import argparse

import dateutil
import dateutil.tz
import lxml.html
import numpy as np
from sklearn import preprocessing

# from svmutil import svm_read_problem

script_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_args():
    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-m', '--mode', default="onetime", dest="mode", help="test mode")
    args = parser.parse_args()  # demo: mode = args.mode
    return args


# 一般矩阵归一化
def my_normalization(data_ary, axis=0):
    # axis = 0 按列归一化; 1时按行归一化
    if axis == 1:
        data_ary = np.matrix(data_ary).T
        ans = preprocessing.scale(data_ary)
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1.0, 1.0))
        ans = min_max_scaler.fit_transform(ans)
        ans = np.matrix(ans).T
        ans = np.array(ans)
    else:
        ans = preprocessing.scale(data_ary)
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1.0, 1.0))
        ans = min_max_scaler.fit_transform(ans)
    return ans


def one_hot(data_ary, one_hot_len):
    # data_ary = array([1,2,3,5,6,7,9])
    # one_hot_len: one_hot最长列
    max_num = np.max(data_ary);
    ans = np.zeros((len(data_ary), one_hot_len), dtype=np.float64)
    for i in range(len(data_ary)):
        ans[i, int(data_ary[i])] = 1.0
    return ans


def re_onehot(data_ary):
    # data_ary = array([[0,0,0,1.0],[1.0,0,0,0],...])
    ans = np.zeros((len(data_ary),), dtype=np.float64)
    for i in range(len(data_ary)):
        for j in range(len(data_ary[i, :])):
            if data_ary[i, j] == 1.0:
                ans[i] = 1.0 * j;
                break;
    return ans


# 将数据写入h5文件
def write2H5(h5DumpFile, data):
    # if not os.path.exists(h5DumpFile): os.makedir(h5DumpFile)
    with h5py.File(h5DumpFile, "w") as f:
        f.create_dataset("data", data=data, dtype=np.float64)


# 将数据从h5文件导出
def readH5(h5DumpFile):
    feat = [];
    with h5py.File(h5DumpFile, "r") as f:
        feat.append(f['data'][:])
    feat = np.concatenate(feat, 1)
    print('readH5 Feature.shape=', feat.shape)
    return feat.astype(np.float64)


# 将dict数据保存到json
def store_json(file_name, data):
    with open(file_name, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4, ensure_ascii=False))


# 将json文件中的数据读取到dict
def load_json(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return data


# 将一个文件copy到指定目录
def moveFileto(sourceDir, targetDir):
    shutil.copy(sourceDir, targetDir)


# 删除目录下的所有文件
def removeDir(dirPath):
    if not os.path.isdir(dirPath): return
    files = os.listdir(dirPath)
    try:
        for file in files:
            filePath = os.path.join(dirPath, file)
            if os.path.isfile(filePath):
                os.remove(filePath)
            elif os.path.isdir(filePath):
                removeDir(filePath)
        os.rmdir(dirPath)
    except Exception():
        print("removeDir exception")


# 尽量等长分割一维数组(最后一组可能会更短)
def list_cut(x, batch_num):
    ans = [[] for i in range(batch_num)]
    for i, item in enumerate(x, 0):
        ans[i % batch_num].append(item)
    return ans


def get_timestamp():
    now = datetime.now(dateutil.tz.tzlocal())
    timestamp = now.strftime('%m_%d_%H_%M')
    return timestamp


def init_seed(RANDOM_SEED=20190314):
    import numpy as np
    import random
    import torch
    from torch import cuda
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)
    cuda.manual_seed(RANDOM_SEED)


# 给定一个list 将这个list随机划分5折，返回索引即可
def k_fold_split_data(items, n_splits=5, shuffle=True, random_state=20190709):
    # type(items)=list
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    kfolds = skf.split(np.zeros((len(items), 2)), np.zeros((len(items),)))
    kfold = []
    for i, (train_index, vali_index) in enumerate(kfolds, 1):
        kfold.append([train_index, vali_index])
    return kfold


def get_dom_tree(page_content):
    utf8_parser = lxml.html.HTMLParser(encoding='utf-8')
    dom_tree = lxml.html.document_fromstring(
        page_content.encode('utf-8'), parser=utf8_parser)
    return dom_tree
