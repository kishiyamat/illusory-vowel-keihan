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
from typing import List
import numpy as np
from pathlib import Path
from glob import glob


def load_data(space, cond, delta) -> tuple:
    conds = ["base", "rle", "rle_delta"]
    spaces = ["kinki", "tokyo"]
    assert space in spaces and cond in conds
    project_dir = Path("../")
    data_path = glob(str(project_dir/"model/feature/*.npy"))
    train_path = filter(lambda p: p.split("/")[-1].count("_") == 0, data_path)
    test_path = filter(lambda p: p.split("/")[-1].count("_") >= 1, data_path)
    train_token = [p.split("/")[-1] for p in train_path]
    # filter by space
    accept = {"tokyo": ["HL", "LH", "LHH", "HLL"],
              "kinki": ["HL", "HH", "LH", "LL", "LLH", "LHH", "HLL", "HHL", ]}
    train_token = list(filter(
        lambda s: s.split("-")[1] in accept[space],
        train_token
    ))
    train_x = [np.load(str(project_dir/"model/feature"/t)) for t in train_token]
    train_y = [np.load(str(project_dir/f"model/label_{cond}"/t)) for t in train_token]
    test_x = [np.load(p) for p in test_path]
    return train_x, train_y, test_x, None

# experiment settings
# だいたい20データポイント、つまり
# frame_stride が 25ms なので、一モーラ250ms程度ということになる
# ここで修正できてよかった
params = {
    "space": "tokyo",
    "cond": "base",
    "delta": 10
}

train_x, train_y, test_x, _ = load_data(**params)
# %%
print(train_x[0].shape)
print(train_y[0].shape)
# %%
# https://github.com/kishiyamat/lsj-162-replication/blob/main/src/run.py