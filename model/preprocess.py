# %%
import optuna
from numpy.lib.function_base import percentile
from scipy.signal import find_peaks
from pathlib import Path
from typing import List

import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile as sf
from librosa.core.audio import tone

# %%
csv_name = "axb_list.csv"
project_dir = Path("../")
list_path = project_dir/"src/list"/csv_name
target_cols = ["task", "item_id", "type", "a", "x",
               "b", "correct", "item_a", "item_x", "item_b"]
csv_df = pd.read_csv(list_path)[target_cols]
tone_df = csv_df.query("type=='filler'")
train_wav_list = list(filter(lambda s: s.count("_") == 0, set(
    tone_df.a.values.tolist() + tone_df.x.values.tolist() + tone_df.b.values.tolist())))
test_wav_list = list(filter(lambda s: s.count("_") != 0, set(
    tone_df.a.values.tolist() + tone_df.x.values.tolist() + tone_df.b.values.tolist())))
# %%
print(f"train wav files are:\n\t{train_wav_list}")
print(f"test wav files are:\n\t{test_wav_list}")
# %%
# Down-sampling and save
SR = 16_000
for wav_i in train_wav_list+test_wav_list:
    wav_i_path = project_dir/"src/audio/output"/wav_i
    save_path_i = project_dir / "model/wav" / wav_i
    y, sr = librosa.load(wav_i_path, sr=None)  # none にすると読んでくれる
    y_16k = librosa.resample(y, sr, SR)
    sf.write(save_path_i, y_16k, SR)
# %%
# 2. Feature Extraction(f0, rms)
# ここらへん、ハイパラになるかも。
frame_stride = 0.025  # (25ms)
# load
for wav_i in train_wav_list:
    resample_path_i = project_dir / "model/wav" / wav_i
    save_path_i = project_dir / "model/wav" / wav_i
    y, sr = librosa.load(resample_path_i, sr=SR)  # none にすると読んでくれる
    assert sr == SR
    hop_length = int(frame_stride*sr)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz(
        'C2'), fmax=librosa.note_to_hz('C7'), sr=sr, hop_length=hop_length)
    f0 = f0.reshape(1, -1)
    # RMS value for each frame
    rms = librosa.feature.rms(y=y, hop_length=hop_length)  # 音量の計算
    feature = np.concatenate([f0, rms])
    file_name = wav_i.split(".")[0]
    save_path_i = project_dir / "model/feature" / file_name
    np.save(save_path_i, feature, allow_pickle=False)

# %%
# 3. Labeling
# wavの名前から作成する
# window関数とパラメータをチューニングしてうまく割る
def objective(trial):
    n_correct = 0
    # params(find_peaksは色々試した)
    beta = trial.suggest_uniform("beta", 0.5, 2)
    percentile_lower = trial.suggest_int("percentile_lower", 10, 50)
    for wav_i in train_wav_list:  # [:1]:
        file_name = wav_i.split(".")[0]+".npy"
        arr_i_path = project_dir / "model/feature" / file_name
        x = np.load(arr_i_path, allow_pickle=False)[1, :]
        # 境界値が不安定なため、窓がないと1にはならない.
        window = 1-np.kaiser(len(x), beta=beta)
        x = x + window
        _, height = np.percentile(x, [75, percentile_lower])
        peaks, _ = find_peaks(-x, height=-height,)
        label_i = wav_i.split("-")[1]
        n_mora = len(label_i)
        n_peak = len(peaks)
        n_split = n_mora-1
        n_correct += n_split == n_peak

    return n_correct/len(train_wav_list)


study = optuna.create_study(
    direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=100)
# ALL GREEEN
# %%
study.best_params
best_params = study.best_params
print(best_params)
# %%
set([wav_i.split("-")[1] for wav_i in train_wav_list])
cond_mapper = {
    "HHL": {"base": "HHL", "rle": ["H2", "H2", "L1"], "rle_delta": ["H2", "H2", "dL1"]},
    "HL": {"base": "HL", "rle": ["H1", "L1"], "rle_delta": ["H1", "dL1"]},
    "HLL": {"base": "HLL", "rle": ["H1", "L2", "L2"], "rle_delta": ["H1", "dL1", "L1"]},
    "LHH": {"base": "LHH", "rle": ["L1", "H2", "H2"], "rle_delta": ["L1", "dH1", "H1"]},
    "LL": {"base": "LL", "rle": ["L2", "L2"], "rle_delta": ["L2", "L2"]},
    "LLH": {"base": "LLH", "rle": ["L2", "L2", "H1"], "rle_delta": ["L2", "L2", "dH1"]}
}
# %%
# 目視で確認
n_correct = 0
label = []
cond = ["base", "rle", "rle_delta"]
for wav_i in train_wav_list:
    file_name = wav_i.split(".")[0]
    arr_i_path = project_dir / "model/feature" / f"{file_name}.npy"
    x = np.load(arr_i_path, allow_pickle=False)[1, :]
    n_len = len(x)
    window = 1-np.kaiser(n_len, beta=best_params["beta"])
    x = x + window
    _, height = np.percentile(x, [75, best_params["percentile_lower"]])
    peaks, _ = find_peaks(-x, height=-height,)
    # peak に 1 をたてて cumsum して、それをindexにすればいい。
    # Plot
    plt.plot(peaks, x[peaks], "xr")
    plt.plot(x)
    plt.plot(window)
    plt.legend(['distance'])
    plt.show()
    # label(index, tone)
    label_i = wav_i.split("-")[1]
    # indexを振る
    tones_idx = np.zeros(n_len)
    tones_idx[peaks] = 1
    tones_idx = np.cumsum(tones_idx, dtype=int)
    for c in cond:
        tones = [cond_mapper[label_i][c][t_i] for t_i in tones_idx]
        save_path_i = project_dir / f"model/label_{c}" / file_name
        np.save(save_path_i, tones, allow_pickle=False)
    n_mora = len(label_i)
    n_split = n_mora-1
    print(file_name, f"\n\t{n_split} -> {len(peaks)}")
    # Score
    n_correct += n_split == len(peaks)

print(n_correct/len(train_wav_list))