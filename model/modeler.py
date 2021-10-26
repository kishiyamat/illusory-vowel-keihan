from typing import List

import matplotlib.pyplot as plt
import more_itertools
import numpy as np
import rle
from hsmmlearn.hsmm import GaussianHSMM, MultivariateGaussianHSMM

from preprocessor import Preprocessor


class Modeler:
    def __init__(self, area, feature, encoding, **kwargs):
        # TODO: 全てのKでsortを保証
        self.area, self.feature, self.encoding = area, feature, encoding
        self.kwargs = kwargs
        self.feature_label = feature.split(":")
        self.is_multi = len(feature.split(":")) >= 2
        self.model_params = {}
        self.log = ""
        self.dur_std = None
        self.resolusion = 4
        self.hsmm = None
        self.K = []
        # その他のあり得るハイパラ
        # - meanにするか、medianにするか(meanにするには0が多い)
        # - scaleも調整が必要
        # - 持続時間の分布の形状(poisson, 経験)
        # - frame_width

    def fit(self, X: List[np.ndarray], y: List[np.ndarray]) -> None:
        """
        X: 観測数ごとにListにした (n_features, n_samples)
        y: 観測数ごとにListにした(n_samples, )
        """
        # Alpha(射出確率)
        # カテゴリーごとにXを取得して射出確率の計算に使う
        K = list(set(np.concatenate(y)))  # ordered list
        K.sort()
        self.K = K
        X_by_K = self._X_by_K(X, y, K)
        # feature によって射出モデルとパラメータは変わる
        params = {}
        if not self.is_multi:
            params["means"] = np.array([np.mean(X_by_K[K_i]) for K_i in K])
            params["scales"] = np.array([np.std(X_by_K[K_i]) for K_i in K])
        elif self.is_multi:
            params["means"] = [np.mean(X_by_K[K_i], axis=1) for K_i in K]
            params["cov_list"] = [np.cov(X_by_K[K_i]) for K_i in K]  # 2次元の時
        # Beta(遷移確率)
        startprob, tmat = self._startprob_tmat(y, K)
        params["tmat"] = tmat
        params["startprob"] = startprob
        # Duration
        duration_by_K = self._duration_by_K(y, K)
        dur_std_mean = np.mean([np.std(duration_by_K[k]) for k in K])
        self._dur_std_mean = dur_std_mean
        durations = np.concatenate([v for _, v in duration_by_K.items()])
        dur_max = np.max(durations)  # 24のbinがあるこれを1/4のサイズにする。
        # dur_max に std のint分は上限を追加する
        params["durations"] = np.array(
            [self._duration_dist(duration_by_K[k], dur_max+int(dur_std_mean), self.resolusion)
             for k in K]
        )
        self.model_params = params
        if not self.is_multi:
            self.hsmm = GaussianHSMM(**params)
        elif self.is_multi:
            self.hsmm = MultivariateGaussianHSMM(**params)
        return self.hsmm

    def predict(self, X, visual=False):
        """
        X: 入力
            if not sllf.is_multi: (n_sample, )
            if not sllf.is_multi: (n_sample, n_feature)
        """
        y_pred = self.hsmm.decode(X)  # index
        y_pred = np.array(self.K)[y_pred]  # label
        if visual:
            fig, axs = plt.subplots(2)
            fig.suptitle('Vertically stacked subplots')
            time = [i*Preprocessor.frame_stride *
                    1_000 for i in range(len(y_pred))]
            label = self.feature_label
            for idx, tone_label in enumerate(label):
                if self.is_multi:
                    # 多次元の描画
                    axs[0].plot(time, X[:, idx], label=tone_label)
                else:
                    axs[0].plot(time, X, label=tone_label)
                axs[0].set_ylabel("(Hz)")
                axs[0].legend()
            y_set = set(y_pred)
            for label_i in y_set:
                # 非該当にはnanを置く
                low_high = [
                    y_i.count("H") if y_i == label_i else np.nan
                    for y_i in y_pred
                ]  # 0--1
                axs[1].plot(time, low_high, label=label_i)
                axs[1].set_ylabel("Pitch")
                axs[1].legend()
                axs[1].set_xlabel("(ms)")
            plt.show()
        return y_pred

    @staticmethod
    def to_pattern(y_seq: List[str]) -> str:
        """
        y_seq: ["H2", "H2", "H2", "dL1", "dL1"] など
        """
        seq, _ = rle.encode(y_seq)
        seq = [seq_i.replace("d", "")for seq_i in seq]
        res = []
        for seq_i in seq:
            assert len(seq_i) == 2  # 各系列(d抜き)は長さ2
            pitch, length = seq_i[0], seq_i[1]
            res.extend([pitch]*int(length))
        return "".join(res)

    def duration_log(self):
        # log
        frame_stride = Preprocessor.frame_stride  # 0.025
        print("std of frame duration is ", round(self._dur_std_mean, 2))
        print(f"since the frame_stride is {frame_stride}(s)")
        print(
            f"the 2*sd of duraion is {round(2*self._dur_std_mean*frame_stride, 2)}(s)"
        )
        print("assuming that the distribution is bellcurve")
        print(
            f"the resolution is set to {self.resolusion}, which is supposed to be 2*sd"
        )

    @staticmethod
    def _X_by_K(X: List[np.ndarray], y: List[np.ndarray], K: list) -> dict:
        assert more_itertools.is_sorted(K)
        X_by_K = {k: [] for k in K}
        for k in K:
            # シンボルkの辞書を観測iごとに更新していく
            for X_i, y_i in zip(X, y):
                X_by_K[k] = X_by_K[k] + \
                    [X_i[:, y_i == k]]
            # まとめ終わったらconcateする(n_feature, n_sample)
            X_by_K[k] = np.concatenate(X_by_K[k], axis=1)
        return X_by_K

    @staticmethod
    def _duration_by_K(y: List[np.ndarray], K: list) -> dict:
        duration_by_K = {k: [] for k in K}
        for y_i in y:
            # 2. 各観測 y_i で rle し、カテゴリーの系列を取得、silを先頭に足す
            seq, duration = rle.encode(y_i)
            for s, d in zip(seq, duration):
                duration_by_K[s] = duration_by_K[s]+[d]
        return duration_by_K

    @staticmethod
    def _startprob_tmat(y: List[np.ndarray], K):
        """
        y: 観測数ごとにListにしたList(n_samples, )
        """
        assert more_itertools.is_sorted(K)
        # 0. np.zerosで K+1 x K+1 の行列を作成(silを足すためK+1になる)
        counter = np.zeros((len(K)+1, len(K)+1), dtype=int)
        # 1. 初期確率を求めるため、カテゴリーにsil(ent)を足す
        K_with_bos = ["bos"] + K  # 最初の確率
        for y_i in y:
            # 2. 各観測 y_i で rle し、カテゴリーの系列を取得、bosを先頭に足す
            seq, _ = rle.encode(y_i)
            seq = ["bos"] + seq
            n_transition = len(seq)-1
            for i in range(n_transition):
                # 3. 系列の [i, i+1] を足していく
                from_idx = K_with_bos.index(seq[i])
                to_idx = K_with_bos.index(seq[i+1])
                counter[from_idx, to_idx] += 1

        # 4. 存在するかしないかの2択なのでboolにしてintにする(0/1)
        counter_bin = counter.astype(bool).astype(int)
        # 5. 確率に変換する: 横に潰してsumして、それを(n_state, 1)にreshapeして除算
        tmat_with_bos = counter_bin / counter_bin.sum(axis=1).reshape(-1, 1)
        startprob = tmat_with_bos[0, 1:]  # 0行,1列以降
        assert np.sum(startprob) == 1
        tmat = tmat_with_bos[1:, 1:]  # 1行,1列以降
        tmat = np.nan_to_num(tmat)
        for idx, row in enumerate(tmat):
            # 6. 和が0の時、自身に遷移させる
            if np.sum(row) == 0:
                row[idx] = 1
            # 7. 遷移確率の和が1を保証
            assert np.sum(row) == 1
        return startprob, tmat

    @staticmethod
    def _duration_dist(arr, max, res):
        """
        arr: 求めたい分布のarr
        max: クラスK_i の arr だけではなく、全Kのarrのmax
        res: 1塊とするframeの個数
            strideが25msでresが4のとき、100msをひとかたまりとする。
            このresの値はbelcurveの時の sd の 2倍が適切
        """
        count, _ = np.histogram(arr, bins=int(max/res), range=(1, max))
        count = count/res  # resで割っておく
        x = np.concatenate([[i]*res for i in count])
        duration = x/np.sum(x)
        assert np.isclose(np.sum(duration), 1, rtol=1e-10, atol=1e-10)
        return duration
