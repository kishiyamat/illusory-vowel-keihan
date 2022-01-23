# %%
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from multiprocessing import Pipe
from sklearn.cluster import KMeans
import itertools

import librosa
import numpy as np
import pandas as pd
import parselmouth
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from plotnine import *
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline

from modeler import Modeler
from path_manager import PathManager

# %%
# 1. HSMM
# 2. tokyo_kinki_ratio
# 3.


class DataLoader:
    def __init__(self, feature_type):
        self.feature_type = feature_type
        pass


class Model:
    def __init__(self, use_semitone: bool, use_duration: bool, use_transition: bool, tokyo_kinki_ratio: float):
        """[summary]

        Args:
            use_semitone (bool): [特徴量としてsemitoneを利用するか]
            use_duration (bool): [ラベルに持続時間を埋め込むか: HHをH2とするかHHとするか]
            use_transition (bool): [遷移確率を利用するか: P(H->L2)とP(H2->L)を一様とするか]
            tokyo_kinki_ratio (float): [行動実験の要因とされた東京に居住した割合]
        """
        self.use_semitone = use_semitone
        self.use_duration = use_duration
        self.use_transition = use_transition
        self.tokyo_kinki_ratio = tokyo_kinki_ratio

    def fit(self):
        # 条件によって fit する音響モデルが異なる
        pass

    def predict(self):
        # semitoneとかそこらへんもしっかりキャッチする
        # 入力と出力は合わせる
        pass


# %%
# test_y は axb の x に相当するかと
train_x, train_y, test_x, test_y = DataLoader.laod()
# %%
use_semitones = [True, False]
use_durations = [True, False]
use_transitions = [True, False]
tokyo_kinki_ratios = np.arange(-1.0, 1.1, 0.5)  # 1を含めて0.5刻みの-1から1 -> len==5
# %%
conditions = itertools.product(
    use_semitones,
    use_durations,
    use_transitions,
    tokyo_kinki_ratios,
)
for use_semitone, use_duration, use_transition, tokyo_kinki_ratio in list(conditions):
    model = Model(use_semitone, use_duration,
                  use_transition, tokyo_kinki_ratio)
    model.fit(train_x, train_y)
    print(model)

# %%
# おそらく train は無声化しないデータになっている。
train_wav_list, test_wav_list = PathManager.train_test_wav()
data_list = []

for wav_i in train_wav_list+test_wav_list:
    phoneme, label_all, speaker = wav_i.split("-")
    vowels = "".join(label_all.split("_"))
    n_vowel = len(vowels)
    snd = parselmouth.Sound(str(PathManager.data_path("downsample", wav_i)))
    # FIXME: pitch_floor と pitch_ceiling は可視化しながら調整
    pitch = snd.to_pitch_ac(pitch_floor=60, pitch_ceiling=200)\
        .selected_array['frequency']
    n_data = len(pitch)
    pitch[pitch == 0] = np.nan  # 0はnanにする
    time = np.arange(n_data)
    pipe = Pipeline([
        ("impute", SimpleImputer(missing_values=np.nan, strategy='mean')),
        ("cluster", KMeans(n_clusters=n_vowel, random_state=0))])
    arr = np.array([pitch > 0, time]).T
    cluster = []
    label = []
    cluster_dict = {}
    for c in pipe.fit_predict(arr):
        if c not in cluster_dict:
            cluster_dict[c] = len(cluster_dict)
        cluster.append(cluster_dict[c])
        label.append(vowels[cluster_dict[c]])
    # クラスタリングは空間的にクラスタリングする
    data = pd.DataFrame({
        "pitch": pitch,
        "tone": 6 * np.log(pitch/np.nanmedian(pitch)) / np.log(2),
        "time": time,
        "cluster": cluster,
        "label": label,
        "phoneme": [phoneme]*n_data,
        "label_all": [label_all]*n_data,
        "speaker": [speaker]*n_data,
    })
    data_list.append(data)
    # g = (
    #     ggplot(data, aes(x='time', y='tone'))
    #     + facet_grid(". ~ cluster")
    #     + geom_point()
    #     + labs(x='time', y='tone')
    # )
    # print(g)

data = pd.concat(data_list)
# %%
p = (ggplot(data, aes(x='time', y='tone', color="label", shape="factor(cluster)"))
     + facet_wrap("~ label_all")
     + geom_point()
     + labs(x='time', y='tone'))
p.save(filename='artifacts/tone_by_cluster.png',
       height=8, width=8, units='in', dpi=1000)
# %%
# Appendix
# Semitoneが1あがると半音あがる. toneは2音あがる
# semitone = lambda x: 12 * np.log(x/base) / np.log(2)
# tone = lambda x: 6 * np.log(x/base) / np.log(2)
# https://www.youtube.com/watch?v=QgEInLU92Ls
# 1あがると半音あがる、そんな指標


def tone(pitch, base): return 6 * np.log(pitch/base) / np.log(2),


do = 130.813
do_sharp = 138.591
re = 146.832
tone(re, do)
# %%


# %%

# %%
(
    ggplot(mpg, aes(x='displ', y='hwy'))
    + geom_point()
    + geom_smooth()
    + labs(x='displacement', y='horsepower')
)
