# %%
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

# Footnote
# Semitoneも使った、Durationのエンコーディングなしも使った
use_semitones = [True, False]
use_durations = [True, False]  # Falseは話にならない
use_transitions = [True, False]  # topdown の検証用パラメータ
tokyo_kinki_ratios = [-1,-0.5, 0,0.5, 1]

conditions = itertools.product(
    use_semitones,
    use_durations,
    use_transitions,
    tokyo_kinki_ratios,
)
# %%
# n_participants * n_conditions の実験
n_subjects = 10  # 20ずつ

res = []
for use_semitone, use_duration, use_transition, tokyo_kinki_ratio in list(conditions):
    # Participants
    # 実質、被験者は一人なのでもう少しバラす
    for subj_idx in range(n_subjects):
        model = Model(use_semitone,
                      use_duration,
                      use_transition,
                      tokyo_kinki_ratio,
                      subj_idx=subj_idx,
                      train_ratio = 0.98,
                      tmat_noise_ratio=0.4)
        X, y = model.df2xy(train_df)
        model.fit(X, y)
        # Stimuli
        for _, df_by_stimuli in test_df_3mora.groupby("stimuli"):
            stimulus = df_by_stimuli.stimuli[0].split('.')[0]
            phoneme, pitch, speaker = stimulus.split("-")
            X, _ = model.df2xy(df_by_stimuli)
            X_flatten = np.concatenate(X)  # 実際の入力は区切られていないのでflatten
            y = model.percept(X_flatten)
            y_collapsed = tuple(rle.encode(y)[0])
            is_tokyo = y_collapsed in model.tokyo_pattern
            # そもそも推論に失敗したパターン
            n_fail = model.mora(y_collapsed) != 3
            # AXB で提示したのは東京にとって排他的な HHL など
            # is_kinki = y_collapsed in model.kinki_pattern
            is_kinki = y_collapsed in model.ex_kinki_pattern
            res.append(pd.DataFrame(dict(
                tokyo_pref=[is_tokyo - is_kinki],
                subj_id=[subj_idx],
                stimulus=[stimulus],
                phoneme=[phoneme],
                pitch=[pitch],
                speaker=[speaker],
                use_semitone=[use_semitone],
                use_duration=[use_duration],
                use_transition=[use_transition],
                tokyo_kinki_ratio=[tokyo_kinki_ratio],
                n_fail=[n_fail],
                pred=["".join(y_collapsed)],
            )))

# %%
res_df = pd.concat(res)
# %%
conditions = ["use_semitone", "use_duration", "use_transition"]
plot_df = res_df.groupby(
    conditions+["tokyo_kinki_ratio", "pitch", "phoneme", "subj_id"]).mean().reset_index()
# %%
plot_df
# %%
# transition がなくても右肩上がりの図は再現される...？
# 音響モデルとdurationで、ということになる。
for cond, df_g in plot_df.groupby(["use_semitone", "use_duration", "use_transition"]):
    print(df_g.head())
    n_fail = np.mean(df_g.n_fail)
    print(len(df_g))
    "use_semitone", "use_duration", "use_transition"
    print(cond)
    g = (ggplot(df_g, aes(x='factor(tokyo_kinki_ratio)', y='tokyo_pref', color="pitch", fill="pitch"))
         + facet_grid("pitch~phoneme")
         + geom_violin()
         + ylim(-1, 1)
         + ggtitle(f"n_fail: {n_fail}")
         )
    print(g)

# TODO
# - 統計用のdfを出力
# - 統計で再現
# %%
