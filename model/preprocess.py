# %%
import random
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
import parselmouth
import soundfile as sf
from scipy.signal import find_peaks


def random_resampling(arr_1d, N, it=100):
    # 条件
    # 1. 定常性を仮定できる
    # 1. len(arr_1d) < N:
    # len(arr_1d) と N の差が開くほど精度は落ちる
    if len(arr_1d) < N:
        raise ValueError

    arr_list = []
    for _ in range(it):
        idx = random.sample(list(range(len(arr_1d))), N)
        idx.sort()
        arr_list.append(arr_1d[idx])

    return np.median(np.array(arr_list), axis=0)

# %%


def data_path(wav_path, data_type):
    # p.stem
    # TODO: add test
    project_dir = Path("../")
    accepted_types = [
        "original", "downsample", "feature",
        "label_base", "label_rle", "label_rle_delta"
    ]
    assert data_type in accepted_types
    data_path_map = {
        "original": project_dir / "src/audio/output" / wav_path,
        "downsample": project_dir / "model/wav" / wav_path,
        "feature": project_dir / "model/feature" / str(wav_path.split(".")[0]+".npy"),
        "label_base": project_dir / "model/label_base" / str(wav_path.split(".")[0]+".npy"),
        "label_rle": project_dir / "model/label_rle" / str(wav_path.split(".")[0]+".npy"),
        "label_rle_delta": project_dir / "model/label_rle_delta" / str(wav_path.split(".")[0]+".npy"),
    }
    return data_path_map[data_type]


# %%
# Get Train/Test dataset
project_dir = Path("../")
csv_name = "axb_list.csv"
list_path = project_dir/"src/list"/csv_name
tone_df = pd.read_csv(list_path)[["type", "a", "x", "b"]]\
    .query("type=='filler'")
wav_list_set = set(
    tone_df.a.values.tolist() +
    tone_df.x.values.tolist() +
    tone_df.b.values.tolist()
)
# _を含むのはH_Lのようなテストデータ
train_wav_list = list(filter(lambda s: s.count("_") == 0, wav_list_set))
test_wav_list = list(filter(lambda s: s.count("_") != 0, wav_list_set))

print(f"train wav files are:\n\t{train_wav_list}")
print(f"test wav files are:\n\t{test_wav_list}")

# %%
# %%
# Down-sampling and save
SR = 16_000
for wav_i in train_wav_list + test_wav_list:
    y, sr = librosa.load(data_path(wav_i, "original"), sr=None)
    y_16k = librosa.resample(y, sr, SR)
    sf.write(data_path(wav_i, "downsample"), y_16k, SR)
# %%
# 2. Feature Extraction(f0, rms)
# この段階でハイパラを決める.
# 原理上、理想のf0とrmsの数は決定する
check = ["esuko-HHL-3.wav", "etsuto-LHH-3.wav"]

# %%
# 2. Feature Extraction(f0, rms)
# praat-parselmouth を使ったほうが良さそう
# この段階でハイパラを決める.
# 原理上、理想のf0とrmsの数は決定する
# きつかったリスト
check = ["esuko-LLH-3.wav", "esuko-HHL-3.wav", "etsuto-LHH-3.wav"]


# for wav_i in check:
for wav_i in train_wav_list:
    frame_stride = 0.025  # (25ms)
    y, sr = librosa.load(data_path(wav_i, "downsample"), SR)
    print("should be size of: ", (len(y)/sr)/frame_stride)
    hop_length = int(frame_stride*sr)
    # 他の特徴料と合わせる
    feature_len = librosa.feature.rms(y=y, hop_length=hop_length).shape[1]
    print("should be size of: ", feature_len)
    print(wav_i)
    # parselmouth
    snd = parselmouth.Sound(str(data_path(wav_i, "downsample")))

    intensity = snd.to_intensity().values.T
    intensity = random_resampling(intensity, feature_len).T

    pitch = snd.to_pitch_ac(
        pitch_floor=40, pitch_ceiling=400).selected_array['frequency']
    pitch = random_resampling(pitch, feature_len).reshape(1, -1)
    feature = np.concatenate((pitch, intensity), 0)
    print(feature.shape)
    np.save(data_path(wav_i, "feature"), feature, allow_pickle=False)

    # plt.plot(intensity.reshape(-1))
    # plt.show()
    # plt.plot(pitch.reshape(-1))
    # plt.show()

# %%
# 3. Labeling
# 3.1 hypara
# 3.2 annotation


def objective(trial):
    # 境界にあるデータが不安定なため、窓を当ててpeakから除外する。
    # find_peaksは色々試したが、結果 percentile_lowerによる heightが大事だった
    # window関数とパラメータをチューニングしてうまく割る
    n_correct = 0
    # params
    beta = trial.suggest_uniform("beta", 0.3, 3)
    percentile_lower = trial.suggest_int("percentile_lower", 5, 60)
    for wav_i in train_wav_list:
        rms = np.load(data_path(wav_i, "feature"), allow_pickle=False)[1, :]
        window = 1-np.kaiser(len(rms), beta=beta)
        rms = rms + window
        _, height = np.percentile(rms, [75, percentile_lower])
        peaks, _ = find_peaks(-rms, height=-height,)
        label_i = wav_i.split("-")[1]
        n_mora, n_peak = len(label_i), len(peaks)
        n_split = n_mora - 1
        n_correct += n_split == n_peak
    return n_correct/len(train_wav_list)


study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42)
)
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
    rms = np.load(data_path(wav_i, "feature"), allow_pickle=False)[1, :]
    window = 1-np.kaiser(len(rms), beta=best_params["beta"])
    rms = rms + window
    _, height = np.percentile(rms, [75, best_params["percentile_lower"]])
    peaks, _ = find_peaks(-rms, height=-height,)
    # show
    plt.plot(peaks, rms[peaks], "xr")
    plt.plot(rms)
    plt.plot(window)
    plt.show()
    # indexを振る
    label_i = wav_i.split("-")[1]
    tones_idx = np.zeros(len(rms))
    tones_idx[peaks] = 1
    tones_idx = np.cumsum(tones_idx, dtype=int)
    for c in cond:
        tones = [cond_mapper[label_i][c][t_i] for t_i in tones_idx]
        np.save(data_path(wav_i, f"label_{c}"), tones, allow_pickle=False)
    n_mora, n_peak = len(label_i), len(peaks)
    n_split = n_mora - 1
    n_correct += n_split == n_peak
    print(wav_i, f"\n\t{n_split} -> {len(peaks)}")

print(n_correct/len(train_wav_list))
