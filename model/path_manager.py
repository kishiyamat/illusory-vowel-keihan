# %%
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

    @property
    def train_test_wav(self):
        # Get Train/Test dataset
        tone_df = pd.read_csv(self.data_path("axb")).query("type=='filler'")
        tone_df = tone_df[["a", "x", "b"]]
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
