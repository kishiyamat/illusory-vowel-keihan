# %%
# 実験(3x3)を2パターン作る
# ラベル要因
# - RLEなし
# - RLEあり
# - RLE+デルタ
# 特徴量要因
# - pitch
# - pitch:delta
# - delta
# 言語モデル
# - Tokyo
# - Kinki
# 実験
# testの音声を与えてみて推論させる。
import rle
import librosa
from hsmmlearn.hsmm import MultivariateGaussianHSMM
import matplotlib.pyplot as plt
import random
from pathlib import Path
from pydoc import resolve
from typing import List

import pandas as pd
import numpy as np

from path_manager import PathManager

# %%
# DataLoad
# NOTE: これが実験ファイルになる. 
# TODO: この実験ファイルに基づいて実験を行ってログする
setting = PathManager.setting_df
setting_dicts = [d.to_dict() for _, d in setting.iterrows()]
sample_i = 8
setting_i = setting_dicts[sample_i]
train_x, train_y, _, _ = PathManager.load_data(**setting_i)

for idx, train_x_i in enumerate(train_x):
    print(f"params: {setting_i}")
    print(f"data index: {idx}")
    print(f"data shape: {train_x_i.shape}")
    print(f"data label: {train_y[idx]}")
    for train_x_i_row in train_x_i:
        plt.plot(train_x_i_row)
        plt.show()
# %%
# ModelFit
# 1. meanにするか、medianにするか
# 1. 次元が1の時(1, n_sample)と2の時で同じ処理ができるか
# シンボルごとにxをまとめる
K = list(set(np.concatenate(train_y)))
train_x_dict = {k:[] for k in K}
for k in K:
    # シンボルkの辞書を観測iごとに更新していく
    for train_x_i, train_y_i in zip(train_x, train_y):
        train_x_dict[k] = train_x_dict[k]+[train_x_i[:, train_y_i==k]]
    # まとめ終わったらconcateする(n_feature, n_sample)
    train_x_dict[k] = np.concatenate(train_x_dict[k], axis=1)
# %%
K_i = 3
print(K[K_i])
plt.plot(train_x_dict[K[K_i]][0,:])
plt.show()
# %%
# 上でラベルごとに行列を抽出したので、meansとscalesを産出
# ただ、scalesは共分散行列の認識だが、あっているかを確認する
# また、一次元のときでも同じ対応ができるかどうかも確認する
# means = 0
# scales = 0
# durations = 0
# tmat = 0
# startprob = 0
# MultivariateGaussianHSMM(means, scales, durations, tmat, startprob)

# print(K)
# Stats
#%%
# list(filter(lambda arr: len(arr), train_x_dict[K[0]]))
# %%
# Model Making
# https://github.com/kishiyamat/lsj-162-replication/blob/main/src/run.py


class Subject:
    def __init__(self, area, span_tokyo, span_kinki, encoding, delta, pid) -> None:
        self.__pid = pid
        self.__area = area
        self.__span_tokyo = span_tokyo
        self.__span_kinki = span_kinki
        self.__encoding = encoding
        self.__delta = delta

    @property
    def pid(self):
        # validate
        return self.__pid

    def fit(self, X, y):
        # 読むのは外で一回にする(被験者分のCSJは困る)。
        pass

    def perception(self, X):
        # シンボルの推定
        # dH1などとなるので、注意する
        pass

    def acoustic_diff(self, s_i, s_j):
        # 音響的な違い
        pass

    def axb(self, a, x, b):
        sym_a = self.perception(a)
        sym_x = self.perception(x)
        sym_b = self.perception(b)
        # もしかしたら音響的な違いもチェックしたほうがいいかも?
        if sym_a == sym_x and sym_x != sym_b:
            return "a"
        elif sym_a != sym_x and sym_x == sym_b:
            return "b"
        else:
            # random: aもbも同じ場合, aもbも違う場合
            return random.choice(["a", "b"])


load_data
# %%


class Experiment:
    def __init__(self) -> None:
        self.stimuli = self.set_stimuli()
        self.subjects = self.set_subjects()
        self.results = []

    def set_stimuli(self) -> None:
        # load stimuli list
        self.stimuli = 0

    def set_subjects(self) -> None:
        # load subject list
        self.subjects = 0

    def run(self):
        for subject in self.subjects:
            for stimulus in self.stimuli:
                a, x, b, correct = stimulus
                results_i = subject.axb(a, x, b) == correct
