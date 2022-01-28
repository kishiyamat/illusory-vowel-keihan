# %%
import itertools

import numpy as np
import pandas as pd
import parselmouth
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from plotnine import *
from scipy.stats import poisson
from sklearn import tree
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.mixture import GaussianMixture
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

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
        "silent": np.isnan(pitch),
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
data.head(30)
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
        self.tokyo_kinki_ratio = tokyo_kinki_ratio  # tokyoの影響は必ず入る
        self.n_components = n_components
        self.tmat = None  # blend
        self.le = LabelEncoder()
        self.pipe = Pipeline([
            ("impute", SimpleImputer(missing_values=np.nan, strategy='mean')),
            ("model", tree.DecisionTreeClassifier())
            # ("model", GaussianNB()),
        ])

    @property
    def tmat_kinki(self):
        # TODO: 後で定義
        # self.use_duration = use_duration に依存
        pass

    @property
    def tmat_tokyo(self):
        # TODO: 後で定義
        # self.use_duration = use_duration に依存
        pass

    def fit(self, df: pd.DataFrame):
        X_list = []
        sil_list = []
        y_list = []
        for _, row in df.groupby("stimuli"):
            X_list.extend(row.semitone if self.use_semitone else row.pitch)
            sil_list.extend(row.silent)
            y_i = row.rle_label if self.use_duration else row.label
            y_list.extend(y_i)
        self._X = np.array([X_list, sil_list]).T
        self._y = self.le.fit_transform(np.array(y_list))
        self.pipe.fit(self._X, self._y)
        self._X_scaled = self.pipe[:-1].fit_transform(self._X)
        # Duration
        dur_dict = {"label": [], "duration": []}
        cluster_key = "rle_cluster" if self.use_duration else "cluster"
        for _, row in df.groupby(["stimuli", cluster_key]):
            label, *_ = row.rle_label if self.use_duration else row.label
            dur_dict["label"] += [label]
            dur_dict["duration"] += [len(row)]
        self.dur_dict = dur_dict
        # TMAT
        return self

    def draw_features(self):
        label_name = 'semitone' if self.use_duration else "pitch"
        color_name = "rle_label" if self.use_duration else "label"
        df = pd.DataFrame({label_name: self._X_scaled[:, 0],
                           color_name: self.le.inverse_transform(self._y),
                           'silent': self._X[:, 1]})
        p = (ggplot(df, aes(x=label_name, color=color_name, fill=color_name))
             + facet_grid(f"{color_name} ~ silent")
             + geom_histogram()
             + labs(x=label_name, y="count")
             + scale_y_log10()
             )
        return p

    def draw_duration(self):
        duration_df = pd.DataFrame(self.dur_dict)
        p = (ggplot(duration_df, aes(x='duration', color="label", fill="label"))
             + facet_grid(". ~ label")
             + geom_histogram(bins=20)
             + labs(x='duration', y='count')
             )
        return p

    def predict(self):
        # semitoneとかそこらへんもしっかりキャッチする
        # silはnanで受け取る
        # 入力と出力は合わせる
        pass


# %%
model = Model(use_semitone=True,
              use_duration=True,
              use_transition=True,
              tokyo_kinki_ratio=1.0,
              n_components=3
              )
model.fit(train_df)
print(model.draw_acoustic())
# model.dur_dict
# %%
trues = []
preds = []
for true, pred in zip(model.le.inverse_transform(model._y), model.le.inverse_transform(model.pipe.predict(model._X_scaled))):
    trues.append(true[0])
    preds.append(pred[0])
    print(true, pred)
accuracy_score(trues, preds)
# %%

model.pipe.predict_proba(model._X_scaled)
# %%
print(model.draw_duration())
# %%
duration_df = pd.DataFrame(model.dur_dict)
duration_df.groupby("label").var()
duration_df.groupby("label").mean()
# %%
duration_df


# %%
# Gaussian KDE
# Gaussian Mixture でいいのでは？
X = duration_df.duration.values.reshape(-1, 1)
y = model.le.transform(duration_df.label.values)
print(y)
gm = GaussianMixture(n_components=7, random_state=0)
gm.fit(X, y)
gm.predict_proba(X)
# %%
# %%
# 0とはできない. semitoneの時に別の意味になる。
# nanとはできない. 混合ガウスだから nan はない。
train_df
# p = (ggplot(train_df.fillna(train_df.mean()), aes(x='pitch', color="rle_label", fill="rle_label"))
p = (ggplot(train_df.fillna(train_df.mean()), aes(x='semitone', color="rle_label", fill="rle_label"))
     + facet_grid("rle_label ~ silent")
     + geom_histogram()
     + labs(x='time', y='semitone')
     + scale_y_log10()
     )
print(p)
# p.save(filename='artifacts/tone_by_cluster_rle.png',
#        height=8, width=8, units='cm', dpi=1000)

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
