# %%
import matplotlib.pyplot as plt
import numpy as np
import optuna
from scipy.signal import find_peaks
from path_manager import PathManager


# %%
# 3. Annotation
# 3.1 hypara
# 3.2 annotation


def objective(trial):
    # 境界にあるデータが不安定なため、窓を当ててpeakから除外する。
    # find_peaksは色々試したが、結果 percentile_lowerによる heightが大事だった
    # window関数とパラメータをチューニングしてうまく割る
    n_correct = 0
    # params
    beta = trial.suggest_uniform("beta", 0.3, 3)
    percentile_lower = trial.suggest_int("percentile_lower", 3, 60)
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


# %%
if __name__ == "__main__":
    print()
    # %%
    n_trials = 100
    train_wav_list, _ = PathManager.train_test_wav()
    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    study.optimize(objective, n_trials=n_trials)
    study.best_params
    best_params = study.best_params
    print(best_params)
    print()
    if study.best_value!=1:
        raise ValueError("Try to increse the iteration of resampling in 01_preprocess.py")
    # %%
    set([wav_i.split("-")[1] for wav_i in train_wav_list])
    # %%
    # 目視でアノテーションを確認
    n_correct = 0
    label = []
    encodes = ["base", "rle", "rle_delta"]
    for wav_i in train_wav_list:
        rms = np.load(PathManager.data_path("feature", wav_i),
                      allow_pickle=False
                      )[1, :]
        window = 1-np.kaiser(len(rms), beta=best_params["beta"])
        rms = rms + window
        _, height = np.percentile(rms, [75, best_params["percentile_lower"]])
        peaks, _ = find_peaks(-rms, height=-height,)
        # show
        if 'get_ipython' in globals():
            plt.plot(peaks, rms[peaks], "xr")
            plt.plot(rms)
            plt.plot(window)
            plt.show()
        # indexを振る
        label_i = wav_i.split("-")[1]
        tones_idx = np.zeros(len(rms))
        tones_idx[peaks] = 1
        tones_idx = np.cumsum(tones_idx, dtype=int)
        for encode in encodes:
            tones = [PathManager.label_by_encode[encode][label_i][t_i]
                     for t_i in tones_idx]
            np.save(PathManager.data_path(f"label_{encode}", wav_i),
                    tones, allow_pickle=False
                    )
        n_mora, n_peak = len(label_i), len(peaks)
        n_split = n_mora - 1
        n_correct += n_split == n_peak
        print(wav_i, f"\n\t{n_split} -> {len(peaks)}")

    print(n_correct/len(train_wav_list))
    # 精度が1であることを保証
