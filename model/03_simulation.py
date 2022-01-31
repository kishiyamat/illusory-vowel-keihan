# %%
%load_ext autoreload
%autoreload 2

import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rle
from plotnine import *

from models import Model

# %%
data = pd.read_csv('artifacts/data.csv')
train_df = data.query("is_train == True")
test_df = data.query("is_train == False")

# model make
# TODO
# 1. duration False の時の tmat がおかしい->表示すると変に見えるだけだった
# 1. df から特徴量を生成する過程がややこしい
model = Model(use_semitone=True,
              use_duration=True,
              use_transition=True,
              tokyo_kinki_ratio=1,
              )
# 直感に反するが、
# [
#  [[1, 0],
#   [1, 0],
#   [1, 0],],
#  [[1, 0],
#   [1, 0],],
#  :
# ]
# と
# [[y, y, y], [y, y],...] のようになっていれば良いのでは？
X, y = model.df2arrlist(train_df)
model.fit(X, y)
# %%
test_df["mora"] = test_df.collapsed_pitches.apply(len)
test_df_3mora = test_df.query("mora==3")

col_pitches = []
file_names = []

for _, row in test_df_3mora.groupby("stimuli"):
    col_pitches.append(row.collapsed_pitches[0])
    file_names.append(row.stimuli[0])
test_df_3mora
# %%
test_id = 1  # 11が最大idx
print(file_names[test_id])
print(col_pitches[test_id])
test_df_i = test_df_3mora.query(f'stimuli=="{file_names[test_id]}"')

X, _ = model.df2arrlist(test_df_i)
X_imputed = model.acoustic.imputer.transform(X)
print(rle.encode(model.le.inverse_transform(model.hsmm.decode(X_imputed))))
print(model.le.classes_)
print(plt.imshow(model.acoustic.likelihood(X_imputed)))
plt.show()
print(model.tmat)
print(model.startprob)
print(plt.imshow(model.duration))
plt.show()

# %%
model.pattern2bigram(model.pitch_pattern)
model.tmat
# %%


def draw_features(self):
    label_name = 'semitone' if self.use_duration else "pitch"
    color_name = "rle_label" if self.use_duration else "label"
    df = pd.DataFrame({label_name: self._X_imputed[:, 0],
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
    p = (ggplot(self.dur_df, aes(x='duration', color="label", fill="label"))
         + facet_grid(". ~ label")
         + geom_histogram(bins=20)
         + labs(x='duration', y='count')
         )
    return p


# %%
# 音響モデル
# HHL か H2L1かだから、bell-curve でいいのか
trues = []
preds = []
for true, pred in zip(model.le.inverse_transform(model._y), model.le.inverse_transform(model.acoustic.predict(model._X_imputed))):
    trues.append(true[0])
    preds.append(pred[0])
# semitone使わない方がセグメンタルには性能高い？
# dt: 0.7383720930232558
# nb: 0.7151162790697675

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
    model.fit(train_df)
