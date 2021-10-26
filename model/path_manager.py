# %%
import numpy as np
from glob import glob
from pathlib import Path
import pandas as pd


class PathManager:
    project_dir = Path("../")
    label_by_encode = {
        "base": {
            "HL": "HL",
            "HHL": "HHL",
            "HLL": "HLL",
            "LL": "LL",
            "LHH": "LHH",
            "LLH": "LLH",
        },
        "rle": {
            "HL": ["H1", "L1"],
            "HHL": ["H2", "H2", "L1"],
            "HLL": ["H1", "L2", "L2"],
            "LL": ["L2", "L2"],
            "LHH": ["L1", "H2", "H2"],
            "LLH": ["L2", "L2", "H1"],
        },
        "rle_delta": {
            "HL": ["H1", "dL1"],
            "HHL": ["H2", "H2", "dL1"],
            "HLL": ["H1", "dL1", "L1"],
            "LL": ["L2", "L2"],
            "LHH": ["L1", "dH1", "H1"],
            "LLH": ["L2", "L2", "dH1"],
        },
    }
    accept = {"tokyo": ["HL", "LH", "LHH", "HLL"],
              # HLL を許すとHLLになる。むしろ、話者もそうなのか？
              "kinki": ["HL", "HH", "LH", "LL", "LLH", "HLL", "HHL", ]}
    tone_df = pd.read_csv(project_dir/"src/list/axb_list.csv")\
        .query("type=='filler'")
    setting_df = pd.read_csv(project_dir/"model/setting.csv")

    @classmethod
    def data_path(cls, data_type, wav_path=""):
        """
        wav_path: wav_path じゃなくても良い(どのみち処理するので)
        """
        # 参照したいタイプを渡すとパスを返す
        project_dir = cls.project_dir
        # NOTE: 予測に失敗した時、近畿のLHH拒否が原因かもしれない
        accepted_types = [
            "original", "downsample", "feature", "pitch_delta",
            "label_base", "label_rle", "label_rle_delta",
            "axb",
        ]
        assert data_type in accepted_types
        data_path_map = {
            "original": project_dir / "src/audio/output" / wav_path,
            "downsample": project_dir / "model/wav" / wav_path,
            "feature": project_dir / "model/feature" / str(wav_path.split(".")[0]+".npy"),
            "pitch_delta": project_dir / "model/pitch_delta" / str(wav_path.split(".")[0]+".npy"),
            "label_base": project_dir / "model/label_base" / str(wav_path.split(".")[0]+".npy"),
            "label_rle": project_dir / "model/label_rle" / str(wav_path.split(".")[0]+".npy"),
            "label_rle_delta": project_dir / "model/label_rle_delta" / str(wav_path.split(".")[0]+".npy"),
        }
        return data_path_map[data_type]

    @classmethod
    def train_test_wav(cls):
        tone_df = cls.tone_df[["a", "x", "b"]]
        wav_list_set = set(
            tone_df.a.values.tolist() +
            tone_df.x.values.tolist() +
            tone_df.b.values.tolist()
        )
        # _を含むのはH_Lのようなテストデータ
        train_wav_list = list(
            filter(lambda s: s.count("_") == 0, wav_list_set))
        test_wav_list = list(filter(lambda s: s.count("_") != 0, wav_list_set))
        return train_wav_list, test_wav_list

    @staticmethod
    def is_illusory(path) -> bool:
        """
        hoge/hoge.x -> false
        hoge/ho_ge.x -> true
        """
        return bool(path.split("/")[-1].count("_"))

    @staticmethod
    def is_not_illusory(path) -> bool:
        """
        hoge/hoge.x -> true
        hoge/ho_ge.x -> false
        """
        return not bool(path.split("/")[-1].count("_"))

    @classmethod
    def load_data(cls, area, encoding, feature, **kwargs) -> tuple:
        # check if the settings are just right
        spaces = ["kinki", "tokyo"]
        encoding_methods = ["base", "rle", "rle_delta"]
        feature_set = ["pitch", "pitch:pitch_delta", "pitch_delta"]
        assert area in spaces \
            and encoding in encoding_methods \
            and feature in feature_set

        # Get tokens for train and test
        feature_path = glob(str(cls.project_dir/"model/feature/*.npy"))
        pitch_delta_path = glob(str(cls.project_dir/"model/pitch_delta/*.npy"))
        # 前処理が適切なら feature と pitch_delta の数が等しい
        assert len(feature_path) == len(pitch_delta_path)

        # feature_pathからtrainとtestに分ける
        train_path = filter(cls.is_not_illusory, feature_path)
        test_path = filter(cls.is_illusory, feature_path)
        train_token = [p.split("/")[-1] for p in train_path]
        test_token = [p.split("/")[-1] for p in test_path]
        # filter by area: token(LLHなど)が条件(kinki--tokyo)を満たすか
        train_token = list(filter(
            lambda s: s.split("-")[1] in cls.accept[area],
            train_token
        ))
        # Xの組み合わせは3種類ある
        feature_set = ["pitch", "pitch:pitch_delta", "pitch_delta"]
        train_x = []
        for t in train_token:
            pitch = np.load(cls.data_path("feature", t))[0, :].reshape(1, -1)
            delta = np.load(cls.data_path("pitch_delta", t))
            if feature == "pitch":
                train_x.append(pitch)
            elif feature == "pitch:pitch_delta":
                train_x.append(np.concatenate([pitch, delta]))
            elif feature == "pitch_delta":
                train_x.append(delta)
            else:
                raise NotImplementedError

        train_y = [
            np.load(cls.data_path(f"label_{encoding}", t))
            for t in train_token
        ]
        test_x = []
        for t in test_token:
            pitch = np.load(cls.data_path("feature", t))[0, :].reshape(1, -1)
            delta = np.load(cls.data_path("pitch_delta", t))
            # testはそのままdecodeできる値にする。
            # pitch や pitch_delta は GausianHSMM
            # pitch:pitch_delta は Multivariate の入力になる
            if feature == "pitch":
                test_x.append(pitch.flatten())
            elif feature == "pitch:pitch_delta":
                test_x.append(np.concatenate([pitch, delta]).T)
            elif feature == "pitch_delta":
                test_x.append(delta.flatten())
            else:
                raise NotImplementedError
        return train_x, train_y, test_x, test_token
