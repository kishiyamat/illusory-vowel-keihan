# %%
import random

import librosa
import numpy as np


class Preprocessor:
    sr = 16_000
    frame_stride = 0.025  # (25ms)

    @staticmethod
    def random_resampling(arr_1d, N, it=500):
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

        # meanだと0で下がってしまう(nanmedianでもよい)
        return np.median(np.array(arr_list), axis=0)

    @classmethod
    def pitch_intensity(cls, y, sr, snd, resampling_iter, ceiling):
        # ["esuko-LLH-3.wav", "esuko-HHL-3.wav", "etsuto-LHH-3.wav"]
        # を目視で確認しながなら特徴量を選択した。
        # もとは librosa をつかっていたが、 parselmouth に以降
        # ただ、特徴量の幅は librosa に準拠
        # resamplingしないとガタガタでアノテーションができない
        hop_length = int(cls.frame_stride*sr)
        feature_len = librosa.feature.rms(y=y, hop_length=hop_length).shape[1]

        intensity = snd.to_intensity().values.T
        intensity = cls.random_resampling(
            intensity, feature_len, resampling_iter
        ).T

        # ここで決めちゃえばいい？
        pitch = snd.to_pitch_ac(pitch_floor=40, pitch_ceiling=600)\
            .selected_array['frequency']
        pitch[pitch > ceiling] = 0
        pitch = cls.random_resampling(pitch, feature_len).reshape(1, -1)
        return np.concatenate((pitch, intensity), 0)

    @classmethod
    def delta(cls, arr, width=1):
        # deltaの計算
        # naを事前に除去する方法も考えたが、それだと H_L のケースで詰む
        # [1,2,3] ->
        # [1,2,3,0] -> base(add tail)
        # [0,1,2,3] -> refer
        # [1, 1, 1, 3] -> diff
        # [1, 1, 1] -> drop tail
        # v->v のみを計算する
        pad = np.array([0 for _ in range(width)])
        base = np.append(arr, pad)
        refer = np.append(pad, arr)
        # 0をnanに変えて計算を観測値のあるケースでのみ行う
        base[base == 0] = "nan"
        refer[refer == 0] = "nan"
        delta = base - refer
        return delta[:-width]

    @classmethod
    def delta_ensemble(cls, arr, width_list):
        # モーラ数に依存して速度が変わるため、複数の比較をおこなってmedianを取る
        deltas = np.array([cls.delta(arr, width) for width in width_list])
        return np.nanmedian(deltas, axis=0)
