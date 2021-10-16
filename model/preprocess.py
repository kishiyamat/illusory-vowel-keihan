# %%
import random

import librosa
import numpy as np
import parselmouth
import soundfile as sf

from path_manager import PathManager


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


if __name__ == "__main__":
    train_wav_list, test_wav_list = PathManager.train_test_wav
    print(f"train wav files are:\n\t{train_wav_list}")
    print(f"test wav files are:\n\t{test_wav_list}")

    # 1. Down-sampling and save
    SR = 16_000
    for wav_i in train_wav_list + test_wav_list:
        y, sr = librosa.load(PathManager.data_path("original", wav_i), sr=None)
        y_16k = librosa.resample(y, sr, SR)
        sf.write(PathManager.data_path("downsample", wav_i), y_16k, SR)

    # 2. Feature Extraction(pitch, intensity)
    for wav_i in train_wav_list + test_wav_list:
        y, sr = librosa.load(PathManager.data_path("downsample", wav_i), SR)
        snd = parselmouth.Sound(
            str(PathManager.data_path("downsample", wav_i)))
        feature = Preprocessor.pitch_intensity(y, sr, snd)
        np.save(PathManager.data_path("feature", wav_i),
                feature,
                allow_pickle=False)
