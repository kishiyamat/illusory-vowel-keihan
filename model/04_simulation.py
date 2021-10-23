# %%
from path_manager import PathManager
import rle
import librosa
from hsmmlearn.hsmm import MultivariateGaussianHSMM
import matplotlib.pyplot as plt
import random
from pathlib import Path
from pydoc import resolve
from typing import List
from preprocessor import Preprocessor

import pandas as pd
import numpy as np

import pprint
pp = pprint.PrettyPrinter()
# %%
# Setting for experiment
setting = PathManager.setting_df
setting_dicts = [d.to_dict() for _, d in setting.iterrows()]
sample_i = 4
# sample_i = 8
setting_i = setting_dicts[sample_i]
pp.pprint(setting_i)
# %%
# DataLoad
train_x, train_y, _, _ = PathManager.load_data(**setting_i)
# %%
# ModelBuild


class Model:
    def __init__(self, area, feature, encoding, **kwargs):
        self.area, self.feature, self.encoding = area, feature, encoding
        self.kwargs = kwargs
        self.is_multi = len(feature.split(":")) >= 2
        self.params = {}
        # その他のあり得るハイパラ
        # - meanにするか、medianにするか(meanにするには0が多い)
        # - scaleも調整が必要
        # - 持続時間の分布の形状(poisson, 経験)
        # - frame_width

    def fit(self, X: List[np.ndarray], y: List[np.ndarray]) -> None:
        """
        X: 観測数ごとにListにした (n_features, n_samples)
        y: 観測数ごとにListにした(n_samples, )
        """
        # Alpha(射出確率)
        # カテゴリーごとにXを取得して射出確率の計算に使う
        K = list(set(np.concatenate(y)))  # ordered list
        X_by_K = self._X_by_K(X, y, K)
        # feature によって射出モデルとパラメータは変わる
        params = {}
        if not self.is_multi:
            params["model_name"] = "GaussianHSMM"
            params["mean"] = [np.mean(X_by_K[K_i]) for K_i in K]
            params["scales"] = [np.std(X_by_K[K_i]) for K_i in K]
        elif self.is_multi:
            params["model_name"] = "MultivariateGaussianHSMM"
            params["mean"] = [np.mean(X_by_K[K_i], axis=1) for K_i in K]
            params["cov_list"] = [np.cov(X_by_K[K_i]) for K_i in K]  # 2次元の時
        # Beta(遷移確率)
        startprob, tmat = self._startprob_tmat(y, K)
        params["categories"] = K
        params["tmat"] = tmat
        params["startprob"] = startprob
        durations = None
        # MultivariateGaussianHSMM(means, scales, durations, tmat, startprob)
        pp.pprint(params)
        self.params = params
        return self

    @staticmethod
    def _X_by_K(X: List[np.ndarray], y: List[np.ndarray], K: list) -> dict:
        X_by_K = {k: [] for k in K}
        for k in K:
            # シンボルkの辞書を観測iごとに更新していく
            for X_i, y_i in zip(X, y):
                X_by_K[k] = X_by_K[k] + \
                    [X_i[:, y_i == k]]
            # まとめ終わったらconcateする(n_feature, n_sample)
            X_by_K[k] = np.concatenate(X_by_K[k], axis=1)
        return X_by_K

    @staticmethod
    def _duration_by_K(y: List[np.ndarray], K: list) -> dict:
        pass

    @staticmethod
    def _startprob_tmat(y: List[np.ndarray], K):
        """
        y: 観測数ごとにListにしたList(n_samples, )
        """
        # 0. np.zerosで K+1 x K+1 の行列を作成(silを足すためK+1になる)
        counter = np.zeros((len(K)+1, len(K)+1), dtype=int)
        # 1. 初期確率を求めるため、カテゴリーにsil(ent)を足す
        K = ["bos"] + K  # 最初の確率
        for y_i in y:
            # 2. 各観測 y_i で rle し、カテゴリーの系列を取得、bosを先頭に足す
            seq, _ = rle.encode(y_i)
            seq = ["bos"] + seq
            n_transition = len(seq)-1
            for i in range(n_transition):
                # 3. 系列の [i, i+1] を足していく
                from_idx = K.index(seq[i])
                to_idx = K.index(seq[i+1])
                counter[from_idx, to_idx] += 1

        # 4. 存在するかしないかの2択なのでboolにしてintにする(0/1)
        counter_bin = counter.astype(bool).astype(int)
        # 5. 確率に変換する: 横に潰してsumして、それを(n_state, 1)にreshapeして除算
        tmat_with_sil = counter_bin / counter_bin.sum(axis=1).reshape(-1, 1)
        startprob = tmat_with_sil[0, 1:]  # 0行,1列以降
        assert np.sum(startprob) == 1
        tmat = tmat_with_sil[1:, 1:]  # 1行,1列以降
        tmat = np.nan_to_num(tmat)
        for idx, row in enumerate(tmat):
            # 6. 和が0の時、自身に遷移させる
            if np.sum(row) == 0:
                row[idx] = 1
            # 7. 遷移確率の和が1を保証
            assert np.sum(row) == 1
        return startprob, tmat


# %%
model = Model(**setting_i)
model.fit(train_x, train_y)
# %%
# まずKのプレースホルダーを作成
# ポアソンなのか、経験なのか。
# 0の確率は存在しない。1スタート
# 粒度の問題か。
# モーラはxだから、100ms程度で分けて良いだろう。
# ただ、あまりヒューリスティックスには頼りたくない。
# まぁサンプリングしてdiscreteにすればいいか
y = train_y
K = list(set(np.concatenate(y)))  # ordered list
# Kごとにdurationの統計を取る
duration_dist = "hist"

duration_by_K = {k: [] for k in K}
for y_i in y:
    # 2. 各観測 y_i で rle し、カテゴリーの系列を取得、silを先頭に足す
    seq, duration = rle.encode(y_i)
    for s, d in zip(seq, duration):
        duration_by_K[s] = duration_by_K[s]+[d]

dur_means = [np.mean(duration_by_K[k]) for k in K]
dur_std_mean = np.mean([np.std(duration_by_K[k]) for k in K])
frame_stride = Preprocessor.frame_stride  # 0.025
print("std of frame duration is ", round(dur_std_mean, 2))
print(f"since the frame_stride is {frame_stride}(s)")
print(f"the 2*sd of duraion is {round(2*dur_std_mean*frame_stride, 2)}(s)")
print("assuming that the distribution is bellcurve")
resolusion = 4
print(f"the resolution is set to {resolusion}, which is supposed to be 2*sd")

pp.pprint(duration_by_K)
durations = np.concatenate([v for k, v in duration_by_K.items()])
dur_max = np.max(durations)  # 24のbinがあるこれを1/4のサイズにする。


def duration_dist(arr, max, res):
    """
    arr: 求めたい分布のarr
    max: クラスK_i の arr だけではなく、全Kのarrのmax
    res: 1塊とするframeの個数
        strideが25msでresが4のとき、100msをひとかたまりとする。
        このresの値はbelcurveの時の sd の 2倍が適切
    """
    count, _ = np.histogram(arr, bins=int(max/res), range=(1, max))
    print(count)
    count = count/res
    x = np.concatenate([[i]*res for i in count])
    duration = x/np.sum(x)
    assert np.sum(duration) == 1
    return duration


for k in K:
    print(k)
    duration_by_K[k] = duration_dist(duration_by_K[k], dur_max, resolusion)

duration_by_K

# %%
# %%
# ModelFit
# 1. 次元が1の時(1, n_sample)と2の時で同じ処理ができるか
tmat = [[0.5, 0.5],
        [0.5, 0.5]]
dur_dict = {k_i: np.mean([np.sum(y == k_i) for y in train_y])for k_i in K}
dur_dict
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
