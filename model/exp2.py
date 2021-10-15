# %%
# 実験
# モデル作成
# モデル要因
# - Naive Bayes
# - RLEなし
# - RLEあり
# - RLE+デルタ
# ハイパーパラメータ
# - 何個先をdeltaするか
# - 何階deltaとするか
# モデル
# - Tokyo
# - Kinki
# 実験
# testの音声を与えてみて推論させる。
from hsmmlearn.hsmm import MultivariateGaussianHSMM
import matplotlib.pyplot as plt
import random
from glob import glob
from pathlib import Path
from pydoc import resolve
from typing import List

import numpy as np
# %%
# Data Load
setting_i = {
    "area": "tokyo",  # 東京居住歴 (異なるパターンへの許容度)
    "span_tokyo": 10,  # 東京居住歴 (異なるパターンへの許容度)
    "span_kinki": 0,  # 近畿居住歴 (異なるパターンへの許容度)
    "encoding": "base",
    "delta": (10, ),  # どれくらい前を見と比較するのか(単位一つが25ms)
    "pid": 0,
}


def load_data(area, encoding, **kwargs) -> tuple:
    encoding_methods = ["base", "rle", "rle_delta"]
    spaces = ["kinki", "tokyo"]
    assert area in spaces and encoding in encoding_methods
    project_dir = Path("../")
    data_path = glob(str(project_dir/"model/feature/*.npy"))
    train_path = filter(lambda p: p.split("/")[-1].count("_") == 0, data_path)
    test_path = filter(lambda p: p.split("/")[-1].count("_") >= 1, data_path)
    train_token = [p.split("/")[-1] for p in train_path]
    # filter by area
    accept = {"tokyo": ["HL", "LH", "LHH", "HLL"],
              "kinki": ["HL", "HH", "LH", "LL", "LLH", "HLL", "HHL", ]}
    train_token = list(filter(
        lambda s: s.split("-")[1] in accept[area],
        train_token
    ))
    train_x = [np.load(str(project_dir/"model/feature"/t))
               for t in train_token]
    train_y = [
        np.load(str(project_dir/f"model/label_{encoding}"/t)) for t in train_token]
    test_x = [np.load(p) for p in test_path]
    return train_x, train_y, test_x, None


# ((pitch, intensity), ...)
train_x, train_y, _, _ = load_data(**setting_i)
pid_i = setting_i["pid"]
data_i = 8

train_x_i, train_y_i = train_x[data_i], train_y[data_i]
print(train_x_i.shape)
print(train_y_i.shape)
print(train_y_i)
plt.plot(train_x_i[0, :])
plt.show()
plt.plot(train_x_i[1, :])
plt.show()

# %%
# https://github.com/jvkersch/hsmmlearn/blob/master/docs/source/tutorial.rst
# TODO
# - [ ] まずは一人のモデルを作る
# - [ ] デルタを加える
# - [ ] 初期状態と終端状態を加える
# RLEで一発では？(空白区切りじゃないとだめ. )

import rle 
rle.encode(train_y_i)
y_all = []
_ = [y_all.extend(y) for y in train_y]
# y_all ここで y_all で音声を拾えばいい
train_x_i
# 0がある (pitch, intensity). これを
# "delta": (10, ) に基づいて増加させたい
#%%
# deltaの計算
import librosa
# train_x_i
# 10--15で上がってほしい. で、20--は不変であってほしい
# train_x_i[train_x_i==0]= "nan"
# あるいは、nanの部分をtrimするか。
# それいいな。
train_x_i_delta = librosa.feature.delta(train_x_i, width=9)
# X.shape =(d, t)
plt.plot(train_x_i[0, :])
plt.show()
plt.plot(train_x_i[1, :])
plt.show()
plt.plot(train_x_i_delta[0, :])
plt.show()
plt.plot(train_x_i_delta[1, :])
plt.show()
#%%

# means = 0  
# scales = 0
# durations = 0
# tmat = 0
# startprob = 0
# MultivariateGaussianHSMM(means, scales, durations, tmat, startprob)
# %%
# Model Making
# https://github.com/kishiyamat/lsj-162-replication/blob/main/src/run.py


class Subject:
    def __init__(self, area, span_tokyo, span_kinki, encoding, delta, pid) -> None:
        self.pid = pid
        self.area = area
        self.span_tokyo = span_tokyo
        self.span_kinki = span_kinki
        self.encoding = encoding
        self.delta = delta

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
