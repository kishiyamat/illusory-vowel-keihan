# %%
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
import soundfile as sf
from scipy.signal import find_peaks
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
import parselmouth

check = ["esuko-LLH-3.wav", "esuko-HHL-3.wav", "etsuto-LHH-3.wav"]
from scipy import signal
for wav_i in train_wav_list: # [:1]:
# for wav_i in check:
    # wav_i = x 
    # frame_stride = 0.005  # (25ms)
    frame_stride = 0.025  # (25ms)
    y, sr = librosa.load(data_path(wav_i, "downsample"), SR)
    hop_length = int(frame_stride*sr)
    f0, _, voiced_prob = librosa.pyin(
        # https://www.fon.hum.uva.nl/praat/manual/Sound__To_Pitch__ac____.html
        y,
        fmin=20,
        fmax=400,
        sr=sr,
        hop_length=hop_length,
    )
    rms = librosa.feature.rms(y=y, hop_length=hop_length)
    feature = np.concatenate([f0.reshape(1, -1), rms])
    np.save(data_path(wav_i, "feature"), feature, allow_pickle=False)
    # rms = np.load(arr_i_path, allow_pickle=False)[0, :]
    # rms = np.load(arr_i_path, allow_pickle=False)[1, :]
    print(f0.shape)
    print(rms.shape)
    print(wav_i)
    # plt.plot(rms)
    # plt.plot(np.nan_to_num(f0))
    # plt.show()
    # plt.plot(rms.reshape(-1, 1))
    # plt.show()
    # plt.plot(voiced_prob)
    # plt.show()
    # parselmouth
    snd = parselmouth.Sound(str(data_path(wav_i, "downsample")))
    # 
    intensity = snd.to_intensity().values.T
    plt.plot(intensity)
    plt.show()
    plt.plot(signal.resample(intensity, 40))
    plt.show()
    pitch = snd.to_pitch_ac(voicing_threshold=0.5, pitch_ceiling=400).selected_array['frequency']
    plt.plot(signal.resample(pitch, 40))
    plt.show()
    # オクターブジャンプ
    # 外れ値は存在する。しかも上方向にだけ
    plt.plot(pitch)
    plt.show()

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
        "feature": project_dir / "model/feature" / str(wav_i.split(".")[0]+".npy"),
    }
    return data_path_map[data_type]

# %%
# 3. Labeling


def objective(trial):
    # 境界にあるデータが不安定なため、窓を当ててpeakから除外する。
    # find_peaksは色々試したが、結果 percentile_lowerによる heightが大事だった
    # window関数とパラメータをチューニングしてうまく割る
    n_correct = 0
    # params
    beta = trial.suggest_uniform("beta", 0.3, 3)
    percentile_lower = trial.suggest_int("percentile_lower", 5, 60)
    th = trial.suggest_uniform("th", -10, -0)
    dist = trial.suggest_uniform("dist", 1, 20)
    for wav_i in train_wav_list:  # [:1]:
        rms = np.load(data_path(wav_i, "feature"), allow_pickle=False)[1, :]
        window = 1-np.kaiser(len(rms), beta=beta)
        # rms -= window
        _, height = np.percentile(rms, [75, percentile_lower])
        peaks, _ = find_peaks(
            -rms,
            height=-height,
            # threshold=th,
            # distance=dist,
        )
        label_i = wav_i.split("-")[1]
        n_mora, n_peak = len(label_i), len(peaks)
        n_split = n_mora - 1
        n_correct += int(n_split == n_peak)
    return n_correct/len(train_wav_list)


study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42)
)
study.optimize(objective, n_trials=50)
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
    rms = np.load(arr_i_path, allow_pickle=False)[0, :]
    # rms = np.load(arr_i_path, allow_pickle=False)[1, :]
    n_len = len(rms)
    window = 1-np.kaiser(n_len, beta=best_params["beta"])
    rms = rms + window
    _, height = np.percentile(rms, [75, best_params["percentile_lower"]])
    peaks, _ = find_peaks(-rms, height=-height,)
    # peak に 1 をたてて cumsum して、それをindexにすればいい。
    # Plot
    plt.plot(peaks, rms[peaks], "xr")
    plt.plot(rms)
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
        # np.save(save_path_i, tones, allow_pickle=False)
    n_mora = len(label_i)
    n_split = n_mora-1
    print(file_name, f"\n\t{n_split} -> {len(peaks)}")
    # Score
    n_correct += n_split == len(peaks)

print(n_correct/len(train_wav_list))

# %%

# %%
