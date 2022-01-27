# %%
import itertools

import numpy as np
import pandas as pd
import parselmouth
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from plotnine import aes, facet_wrap, geom_point, ggplot, labs, facet_grid
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline


from path_manager import PathManager
from utils import reset_index_by_time, run_length_encode
# %%
train_wav_list, test_wav_list = PathManager.train_test_wav()
data_list = []

check_octave_jump = False
check_clustering = True  # 0か1かで十分分離できる

for wav_i in train_wav_list+test_wav_list:
    # ファイル名から 1. 音素 2. ピッチラベル 3. 話者を取得
    phoneme, collapsed_pitches, speaker = wav_i.split("-")
    vowels = "".join(collapsed_pitches.split("_"))
    # 母音の数を取得(モーラの数ではない cf. esko)
    n_vowel = len(vowels)
    snd = parselmouth.Sound(str(PathManager.data_path("downsample", wav_i)))
    # pitch_floor と pitch_ceiling は可視化して調整(octave jump対策)
    pitch = snd.to_pitch_ac(pitch_floor=60, pitch_ceiling=200)\
        .selected_array['frequency']
    n_data = len(pitch)
    pitch[pitch == 0] = np.nan  # meanの計算で無視するため0はnanにする
    time = np.arange(n_data)  # クラスタリングや可視化で時間の軸が必要になる
    pipe = Pipeline([
        ("impute", SimpleImputer(missing_values=np.nan, strategy='mean')),
        ("cluster", KMeans(n_clusters=n_vowel, random_state=0))])
    arr = np.array([pitch > 0, time]).T
    rle_label_list = run_length_encode(vowels)
    cluster = reset_index_by_time(pipe.fit_predict(arr))
    label = [vowels[cluster_i] for cluster_i in cluster]
    rle_label = [rle_label_list[cluster_i] for cluster_i in cluster]
    # クラスタリングは空間的にクラスタリングする
    data = pd.DataFrame({
        "stimuli": [wav_i] * n_data,
        "is_train": [wav_i in train_wav_list]*n_data,
        "pitch": pitch,
        "tone": 6 * np.log(pitch/np.nanmedian(pitch)) / np.log(2),
        "time": time,
        "cluster": cluster,
        "label": label,
        "rle_label": rle_label,
        "phoneme": [phoneme]*n_data,
        "collapsed_pitches": [collapsed_pitches]*n_data,
        "speaker": [speaker]*n_data,
    })
    data_list.append(data)
    if check_octave_jump or check_clustering:
        g = (
            ggplot(data, aes(x='time', y='tone'))
            + facet_grid(". ~ cluster")
            + geom_point()
            + labs(x='time', y='tone')
        )
        print(g)

data = pd.concat(data_list)
p = (ggplot(data, aes(x='time', y='tone', color="label", shape="factor(cluster)"))
     + facet_wrap("~ collapsed_pitches")
     + geom_point()
     + labs(x='time', y='tone'))
p.save(filename='artifacts/tone_by_cluster.png',
       height=8, width=8, units='in', dpi=1000)

p = (ggplot(data, aes(x='time', y='tone', color="rle_label", shape="factor(cluster)"))
     + facet_wrap("~ collapsed_pitches")
     + geom_point()
     + labs(x='time', y='tone'))
p.save(filename='artifacts/tone_by_cluster_rle.png',
       height=8, width=8, units='in', dpi=1000)

data.to_csv('artifacts/data.csv')
# %%
set(data.query("is_train == True").stimuli)
# %%

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
    model = Model(use_semitone,
                  use_duration,
                  use_transition,
                  tokyo_kinki_ratio)
    model.fit(train_x, train_y)
    print(model)


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
