# %%
# %load_ext autoreload
# %autoreload 2

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
test_df["mora"] = test_df.collapsed_pitches.apply(len)
test_df_3mora = test_df.query("mora==3")

# %%
# 1. 条件でモデルを init -> fit
# 2. 各刺激をmodelに与えて推論
# 3. 推論結果がtokyo_patternかkinki_patternか

use_semitones = [True]
use_durations = [True]  # Falseは話にならない
use_transitions = [True]  # topdown の検証用パラメータ
tokyo_kinki_ratios = [-1, 0, 1]

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
    print(use_semitone, use_duration, use_transition, tokyo_kinki_ratio)
    X, y = model.df2xy(train_df)
    model.fit(X, y)
    y_collapsed_list = []
    for _, df_by_stimuli in test_df_3mora.groupby("stimuli"):
        X, _ = model.df2xy(df_by_stimuli)
        X_flatten = np.concatenate(X)  # 実際の入力は区切られていない
        y = model.percept(X_flatten)
        y_collapsed = tuple(rle.encode(y)[0])
        print("fname:\t", df_by_stimuli.stimuli[0])
        print("pitch:\t", df_by_stimuli.collapsed_pitches[0])
        print("decode:\t", y_collapsed)
        y_collapsed_list.append(y_collapsed)
    n_exp = len(y_collapsed_list)
    n_tokyo = sum([y in model.tokyo_pattern for y in y_collapsed_list ])
    n_kinki = sum([y in model.kinki_pattern for y in y_collapsed_list ])
    print(n_tokyo)
    print(n_kinki)
