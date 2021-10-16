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


class PathManager:
    project_dir = Path("../")

    @classmethod
    def data_path(cls,  data_type, wav_path=""):
        # 参照したいタイプを渡すとパスを返す
        project_dir = cls.project_dir
        accepted_types = [
            "original", "downsample", "feature",
            "label_base", "label_rle", "label_rle_delta",
            "axb",
        ]
        assert data_type in accepted_types
        data_path_map = {
            "original": project_dir / "src/audio/output" / wav_path,
            "downsample": project_dir / "model/wav" / wav_path,
            "feature": project_dir / "model/feature" / str(wav_path.split(".")[0]+".npy"),
            "label_base": project_dir / "model/label_base" / str(wav_path.split(".")[0]+".npy"),
            "label_rle": project_dir / "model/label_rle" / str(wav_path.split(".")[0]+".npy"),
            "label_rle_delta": project_dir / "model/label_rle_delta" / str(wav_path.split(".")[0]+".npy"),
            "axb": project_dir/"src/list/axb_list.csv",
        }
        return data_path_map[data_type]


class Preprocessor:
    sr = 16_000
    frame_stride = 0.025  # (25ms)

    @staticmethod
    def random_resampling(arr_1d, N, it=100):
        # 条件
        # 1. 定常性を仮定できる
        # 1. len(arr_1d) < N:
        # 注意事項
        # 1. len(arr_1d) と N の差が開くほど精度は落ちる
        # 1. グローバルな傾向しか見れない
        if len(arr_1d) < N:
            raise ValueError

        arr_list = []
        for _ in range(it):
            idx = random.sample(list(range(len(arr_1d))), N)
            idx.sort()
            arr_list.append(arr_1d[idx])

        return np.median(np.array(arr_list), axis=0)

    @classmethod
    def pitch_intensity(cls, y, sr, snd):
        # ["esuko-LLH-3.wav", "esuko-HHL-3.wav", "etsuto-LHH-3.wav"]
        # を目視で確認しながなら特徴量を選択した。
        # もとは librosa をつかっていたが、 parselmouth に以降
        # ただ、特徴量の幅は librosa に準拠
        hop_length = int(cls.frame_stride*sr)
        feature_len = librosa.feature.rms(y=y, hop_length=hop_length).shape[1]

        intensity = snd.to_intensity().values.T
        intensity = cls.random_resampling(intensity, feature_len).T

        pitch = snd.to_pitch_ac(pitch_floor=40, pitch_ceiling=400)\
            .selected_array['frequency']
        pitch = cls.random_resampling(pitch, feature_len).reshape(1, -1)
        return np.concatenate((pitch, intensity), 0)


# %%
# Get Train/Test dataset
tone_df = pd.read_csv(PathManager.data_path("axb")).query("type=='filler'")
tone_df = tone_df[["a", "x", "b"]]
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
# 1. Down-sampling and save
SR = 16_000
for wav_i in train_wav_list + test_wav_list:
    y, sr = librosa.load(PathManager.data_path("original", wav_i), sr=None)
    y_16k = librosa.resample(y, sr, SR)
    sf.write(PathManager.data_path("downsample", wav_i), y_16k, SR)

# 2. Feature Extraction(pitch, intensity)
for wav_i in train_wav_list + test_wav_list:
    y, sr = librosa.load(PathManager.data_path("downsample", wav_i), SR)
    snd = parselmouth.Sound(str(PathManager.data_path("downsample", wav_i)))
    feature = Preprocessor.pitch_intensity(y, sr, snd)
    np.save(PathManager.data_path("feature", wav_i),
            feature,
            allow_pickle=False
            )

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
        rms = np.load(PathManager.data_path("feature", wav_i),
                      allow_pickle=False
                      )[1, :]
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
# 目視でアノテーションを確認
n_correct = 0
label = []
cond = ["base", "rle", "rle_delta"]
for wav_i in train_wav_list:
    rms = np.load(PathManager.data_path("feature", wav_i),
                  allow_pickle=False
                  )[1, :]
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
        np.save(PathManager.data_path(f"label_{c}", wav_i),
                tones, allow_pickle=False
                )
    n_mora, n_peak = len(label_i), len(peaks)
    n_split = n_mora - 1
    n_correct += n_split == n_peak
    print(wav_i, f"\n\t{n_split} -> {len(peaks)}")

print(n_correct/len(train_wav_list))
# 精度が1であることを保証

# %%
