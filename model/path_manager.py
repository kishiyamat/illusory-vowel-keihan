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
    tone_df = pd.read_csv(project_dir/"src/list/axb_list.csv")\
        .query("type=='filler'")

    @classmethod
    def data_path(cls, data_type, wav_path=""):
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

    def load_data(area, encoding, **kwargs) -> tuple:
        encoding_methods = ["base", "rle", "rle_delta"]
        spaces = ["kinki", "tokyo"]
        assert area in spaces and encoding in encoding_methods
        project_dir = Path("../")
        data_path = glob(str(project_dir/"model/feature/*.npy"))
        train_path = filter(lambda p: p.split(
            "/")[-1].count("_") == 0, data_path)
        test_path = filter(lambda p: p.split(
            "/")[-1].count("_") >= 1, data_path)
        train_token = [p.split("/")[-1] for p in train_path]
        # filter by area
        # TODO: 予測に失敗した時、近畿のLHH拒否が原因かもしれない
        accept = {"tokyo": ["HL", "LH", "LHH", "HLL"],
                  "kinki": ["HL", "HH", "LH", "LL", "LLH", "HLL", "HHL", ]}
        train_token = list(filter(
            lambda s: s.split("-")[1] in accept[area],
            train_token
        ))
        train_x = [np.load(str(project_dir/"model/feature"/t))
                   for t in train_token]
        train_y = [
            np.load(str(project_dir/f"model/label_{encoding}"/t)) for t in train_token]
        test_x = [np.load(p) for p in test_path]
        return train_x, train_y, test_x, None
