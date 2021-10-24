# %%
import numpy as np
import matplotlib.pyplot as plt
from preprocessor import Preprocessor
import pprint
import random

from modeler import Modeler
from path_manager import PathManager

pp = pprint.PrettyPrinter()
# %%
# Setting for experiment
setting = PathManager.setting_df
setting_dicts = [d.to_dict() for _, d in setting.iterrows()]
condition_i = 8
setting_i = setting_dicts[condition_i]
pp.pprint(setting_i)
# %%
# DataLoad
train_x, train_y, test_x, test_token = PathManager.load_data(**setting_i)
sample_i = 1
print(test_token[sample_i])
print(train_x[sample_i].shape)
print(test_x[sample_i].shape)
# %%
# ModelBuild
model = Modeler(**setting_i)
model.fit(train_x, train_y)
print(setting_i)
print(model.model_params)
test_y = model.hsmm.decode(test_x[sample_i])
print(test_token[sample_i])
y_pred = np.array(model.K)[test_y]
# %%
# まずモーラは錯覚されている。
print(setting_i)
fig, axs = plt.subplots(2)
fig.suptitle('Vertically stacked subplots')
# xはmsに直すと一気にわかりやすくなる
x = [i*Preprocessor.frame_stride*1_000 for i in range(len(y_pred))]
#
label = ["A", "B"] # TODO: model.feature_label を使う
for idx, l in enumerate(label):
    axs[0].plot(x, test_x[sample_i][:, idx], label=l)
    axs[0].legend()
# 非該当にはnanを置く
y_set = set(y_pred)
for l in y_set:
    low_high = [y_i.count("H") if y_i == l else np.nan for y_i in y_pred]  # 0--1
    axs[1].plot(x, low_high, label=l)
    axs[1].legend()
# axs[1].plot(x, y_pred)
plt.show()
# %%
test_x[sample_i].shape
# test_y
# %%
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
