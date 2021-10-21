# %%
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
# sample_i = 0
sample_i = 8
setting_i = setting_dicts[sample_i]
train_x, train_y, _, _ = PathManager.load_data(**setting_i)

# for idx, train_x_i in enumerate(train_x):
#     print(f"params: {setting_i}")
#     print(f"data index: {idx}")
#     print(f"data shape: {train_x_i.shape}")
#     print(f"data label: {train_y[idx]}")
#     for train_x_i_row in train_x_i:
#         if 'get_ipython' in globals():
#             plt.plot(train_x_i_row)
#             plt.show()

# %%


class Model:
    def __init__(self, area, feature, encoding, **kwargs):
        self.area, self.feature, self.encoding = area, feature, encoding
        # その他のあり得るハイパラ
        # meanにするか、medianにするか
        # scaleも調整が必要
        # もしかしたら長さも調整が必要かも
        self.kwargs = kwargs

    def fit(self, X: List[np.ndarray], y: List[np.ndarray]) -> None:
        """
        X: 観測数ごとにListにした (n_features, n_samples)
        y: 観測数ごとにListにした(n_samples, )
        """
        K = list(set(np.concatenate(y)))
        X_by_K = {k: [] for k in K}
        for k in K:
            # シンボルkの辞書を観測iごとに更新していく
            for train_x_i, train_y_i in zip(X, y):
                X_by_K[k] = X_by_K[k] + \
                    [train_x_i[:, train_y_i == k]]
            # まとめ終わったらconcateする(n_feature, n_sample)
            X_by_K[k] = np.concatenate(X_by_K[k], axis=1)

        # feature によって射出モデルのパラメータは変わる
        if self.feature.count(":") == 0:
            means = [np.mean(X_by_K[K_i]) for K_i in K]
            scales = [np.std(X_by_K[K_i]) for K_i in K]  # 2次元の時
            pass
        elif self.feature.count(":") == 1:
            means = [np.mean(X_by_K[K_i], axis=1) for K_i in K]
            scales = [np.cov(X_by_K[K_i]) for K_i in K]  # 2次元の時
            pass
        else:
            raise NotImplementedError
        # area によって遷移確率パラメータは変わるが、yから決まる
        # rle して durは求まる。
        # 早めにK*Kの行列を作る
        tmat = None
        durations = None
        startprob = None
        MultivariateGaussianHSMM(means, scales, durations, tmat, startprob)
        return self


# %%
K = list(set(np.concatenate(train_y)))
K = ["sil"] + K # 最初の確率
K.index("L1")
counter = np.zeros((len(K), len(K)), dtype=int)
for train_y_i in train_y:
    seq, duration = rle.encode(train_y_i)
    seq = ["sil"] + seq
    n_transition = len(seq)-1
    for i in range(n_transition):
        src = K.index(seq[i])
        tgt = K.index(seq[i+1])
        counter[src, tgt] += 1

print(K)
print(counter)
# ラプラスして頻度にする
# 偏りなので0以外は等しい確率を想定する
# sil行はstartprobになる
# sil行、sil列は落とす
# %%
# ModelFit
# 1. 次元が1の時(1, n_sample)と2の時で同じ処理ができるか
tmat = [[0.5, 0.5],
        [0.5, 0.5]]
dur_dict = {k_i: np.mean([np.sum(y == k_i) for y in train_y])for k_i in K}
dur_dict
# %%


def model_select(area, encoding, feature, **kwargs) -> dict:
    pass


# %%
# 上でラベルごとに行列を抽出したので、meansとscalesを産出
# ただ、scalesは共分散行列の認識だが、あっているかを確認する
# MultivariateGaussianHSMM なら cov_list で良い。
# emission を見れば良い
# https://github.com/jvkersch/hsmmlearn/blob/master/docs/source/tutorial.rst で
# For the emission PDFs, we choose clearly separated Gaussians, with means 0, 5, and 10, and standard deviation equal to 1 in each case.
# といっていて、
# scales = np.ones_like(means)としているので sd でよい。これを多次元とするなら、やはり共分散行列
# https://kaisk.hatenadiary.com/entry/2015/02/20/195503
# scale は 標準偏差で良い。
# > The scale (scale) keyword specifies the standard deviation.
# また、一次元のときでも同じ対応ができるかどうかも確認する
  # -> できない。ので、config から条件分岐させる
# %%
# means = 0
# scales = 0
# durations = 0
# tmat = 0
# startprob = 0

# print(K)
# Stats
# %%
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
