# %%
import librosa
import numpy as np
import parselmouth
import soundfile as sf

from path_manager import PathManager
from preprocessor import Preprocessor

# %%
if __name__ == "__main__":
    # 1. Down-sampling and save
    # 2. Feature Extraction(pitch, intensity)
    print()
    # %%
    resampling_iter = 1000
    train_wav_list, test_wav_list = PathManager.train_test_wav()
    print(f"train wav files are:\n\t{train_wav_list}")
    print(f"test wav files are:\n\t{test_wav_list}")

    # 1. Down-sampling and save
    SR = 16_000
    for wav_i in train_wav_list + test_wav_list:
        y, sr = librosa.load(PathManager.data_path("original", wav_i), sr=None)
        y_16k = librosa.resample(y, sr, SR)
        sf.write(PathManager.data_path("downsample", wav_i), y_16k, SR)
    # %%
    # 2. data cleaning
    # データがすくないので外れ値の影響が大きくなるので注意
    import matplotlib.pyplot as plt
    pitch = []
    for wav_i in train_wav_list + test_wav_list:
        snd = parselmouth.Sound(
            str(PathManager.data_path("downsample", wav_i))
        )
        # floor は下げている
        pitch.append(snd.to_pitch_ac(pitch_floor=40, pitch_ceiling=600)
                     .selected_array['frequency'])

    print("Decide th based on histogram.")
    # ここは prompt で入力させてもよいかも
    pitch = np.concatenate(pitch)
    plt.hist(pitch, bins='auto')
    plt.show()
    # まぁ複数のceilingで試してぶれてるやつらは外れ値なんだろうが...
    # ここは図を見て決める
    # ceiling = 300  # (Hz)
    ceiling = float(input("Enter the threshold: "))

    # %%
    # 3. Feature Extraction(pitch, intensity)
    for wav_i in train_wav_list + test_wav_list:
        y, sr = librosa.load(
            PathManager.data_path("downsample", wav_i), SR
        )
        snd = parselmouth.Sound(
            str(PathManager.data_path("downsample", wav_i))
        )
        feature = Preprocessor.pitch_intensity(
            y, sr, snd, resampling_iter, ceiling
            )
        np.save(
            PathManager.data_path("feature", wav_i),
            feature, allow_pickle=False
        )


# %%
