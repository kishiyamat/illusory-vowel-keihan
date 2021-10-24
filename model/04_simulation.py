# %%
import pandas as pd

from modeler import Modeler
from path_manager import PathManager

# %%
# Setting for experiment
# TODO: duration の設定などの追加
if __name__ == "__main__":
    print("04_simulation.py")
    # %%
    setting = PathManager.setting_df
    setting_dicts = [d.to_dict() for _, d in setting.iterrows()]

    results_list = []
    for condition_i, setting_i in enumerate(setting_dicts):
        # DataLoad
        train_x, train_y, test_x, test_token = PathManager.load_data(
            **setting_i)
        # Modeling
        model = Modeler(**setting_i)
        model.fit(train_x, train_y)
        # Experiment
        for sample_idx, test_token_i in enumerate(test_token):
            test_token_i = test_token_i.split(".")[0]  # npyを除外
            phoneme, pitch, speaker = test_token_i.split("-")
            test_y = model.predict(test_x[sample_idx], visual=False)
            res = model.to_pattern(test_y)
            results = {
                "sample_idx": [sample_idx],
                "area": [setting_i["area"]],
                "encoding": [setting_i["encoding"]],
                "feature": [setting_i["feature"]],
                "phoneme": [phoneme],
                "pitch": [pitch],
                "speaker": [speaker],
                "res": [res],
            }
            results_list.append(pd.DataFrame(results))

    results_df = pd.concat(results_list)
    results_df.to_csv("artifacts/results.csv")

# %%
