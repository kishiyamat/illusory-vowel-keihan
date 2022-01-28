# %%
from sklearn import tree
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
check_octave_jump = False
check_clustering = False  # 0か1かで十分分離できる

# %%
train_wav_list, test_wav_list = PathManager.train_test_wav()
data_list = []

for wav_i in train_wav_list + test_wav_list:
    # ファイル名から 1. 音素 2. ピッチラベル 3. 話者を取得
    phoneme, collapsed_pitches, speaker = wav_i.split("-")
    vowels = "".join(collapsed_pitches.split("_"))
    # 母音の数を取得(モーラの数ではない cf. esko)
    n_vowel = len(vowels)
    # pitch_floor と pitch_ceiling は可視化して調整(octave jump対策)
    pitch = parselmouth.Sound(str(PathManager.data_path("downsample", wav_i)))\
        .to_pitch_ac(pitch_floor=60, pitch_ceiling=200)\
        .selected_array['frequency']
    pitch[pitch == 0] = np.nan  # meanの計算/可視化で無視するので0はnanにする
    n_sample = len(pitch)
    time = np.arange(n_sample)  # クラスタリング/可視化で時間の軸が必要になる
    pipe = Pipeline([
        ("impute", SimpleImputer(missing_values=np.nan, strategy='mean')),
        ("cluster", KMeans(n_clusters=n_vowel, random_state=0))])
    arr = np.array([pitch > 0, time]).T  # クラスタリングは0/1の方が好都合
    cluster = reset_index_by_time(pipe.fit_predict(arr))
    label = [vowels[cluster_i] for cluster_i in cluster]
    rle_label = [run_length_encode(vowels)[cluster_i] for cluster_i in cluster]
    data = pd.DataFrame({
        "stimuli": [wav_i] * n_sample,
        "is_train": [wav_i in train_wav_list]*n_sample,
        "pitch": pitch,
        "semitone": 12 * np.log(pitch/np.nanmedian(pitch)) / np.log(2),
        "time": time,
        "cluster": cluster,
        "label": label,
        "rle_cluster": reset_index_by_time(rle_label),
        "rle_label": rle_label,
        "phoneme": [phoneme]*n_sample,
        "collapsed_pitches": [collapsed_pitches]*n_sample,
        "speaker": [speaker]*n_sample,
    })
    data_list.append(data)
    if check_octave_jump or check_clustering:
        g = (
            ggplot(data, aes(x='time', y='semitone'))
            + facet_grid(". ~ cluster")
            + geom_point()
            + labs(x='time', y='semitone')
        )
        print(g)
# %%
# TODO: タイトルの編集
data = pd.concat(data_list)
p = (ggplot(data, aes(x='time', y='semitone', color="label", shape="factor(cluster)"))
     + facet_wrap("~ collapsed_pitches")
     + geom_point()
     + labs(x='time', y='semitone'))
p.save(filename='artifacts/tone_by_cluster.png',
       height=8, width=8, units='cm', dpi=1000)

p = (ggplot(data, aes(x='time', y='semitone', color="rle_label", shape="factor(cluster)"))
     + facet_wrap("~ collapsed_pitches")
     + geom_point()
     + labs(x='time', y='semitone'))
p.save(filename='artifacts/tone_by_cluster_rle.png',
       height=8, width=8, units='cm', dpi=1000)

data.to_csv('artifacts/data.csv')
# %%
# stimuli列ごとに抜き出して学習させれば良い
data.head(20)
# %%
train_df = data.query("is_train == True")
test_df = data.query("is_train == False")
# %%


class Model:
    def __init__(self, use_semitone: bool, use_duration: bool, use_transition: bool, tokyo_kinki_ratio: float, n_components: int):
        """[summary]

        Args:
            use_semitone (bool): [特徴量としてsemitoneを利用(被験者の発話ごとに標準化)するか]
            use_duration (bool): [ラベルに持続時間を埋め込むか: HHをH2とするかHHとするか]
            use_transition (bool): [遷移確率を利用するか: P(H->L2)とP(H2->L)を一様とするか]
            tokyo_kinki_ratio (float): [行動実験の要因とされた東京に居住した割合]
        """
        self.use_semitone = use_semitone
        self.use_duration = use_duration
        self.use_transition = use_transition
        self.tokyo_kinki_ratio = tokyo_kinki_ratio
        # self.n_components = n_components
        self.tmat = None
        self.gm = None

    def fit(self, df: pd.DataFrame):
        X_list = []
        y_list = []
        for _, row in train_df.groupby("stimuli"):
            X_list.extend(row.semitone if self.use_semitone else row.pitch)
            y_i = row.rle_label if self.use_duration else row.label
            y_list.extend(y_i)
        # TODO: silっていう軸を与える
        # で、音声の部分には mean を与えてあげる
        self._X = np.array(X_list, dtype=object).reshape(-1, 1)  # 可視化とかに使える
        self._y = np.array(y_list)
        # self.model = GaussianMixture(n_components=self.n_components, random_state=42)
        self.model = Pipeline([
            ("impute", SimpleImputer(missing_values=np.nan, strategy='constant')),
            ("cluster", KMeans(n_clusters=3, random_state=0)),  # 低い、高い、無し
            ("model", tree.DecisionTreeClassifier())])
        self.model.fit(self._X, self._y)
        self.K = set(y_list)
        # Duration
        dur_dict = {k: [] for k in self.K}
        cluster_key = "rle_cluster" if self.use_duration else "cluster"
        for _, row in train_df.groupby(["stimuli", cluster_key]):
            label, *_ = row.rle_label if self.use_duration else row.label
            dur_dict[label] += [len(row)]
        self.dur_dict = dur_dict
        return self

    def visualize(self):
        pass

    def predict(self):
        # semitoneとかそこらへんもしっかりキャッチする
        # 入力と出力は合わせる
        pass


# %%
model = Model(use_semitone=True,
              use_duration=False,
              use_transition=True,
              tokyo_kinki_ratio=1.0,
              n_components=2
              )
model.fit(train_df)


# %%
X_list = []
for _, row_by_cluster in train_df.groupby(["stimuli", "cluster"]):
    print(set(row_by_cluster.label))
    print(len(row_by_cluster))
    # print(len(idx))
    # print(len(row))
X_list

# %%
# 0とはできない. semitoneの時に別の意味になる。
# nanとはできない. 混合ガウスだから nan はない。
train_df

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
def semitone(pitch, base): return 12 * np.log(pitch/base) / np.log(2),


do = 130.813
do_sharp = 138.591
re = 146.832
print(tone(re, do))
print(semitone(re, do))

# %%
