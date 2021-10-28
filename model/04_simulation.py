# %%
import pandas as pd
from plotnine import (aes, element_text, facet_grid, geom_histogram, ggplot,
                      theme)

from modeler import Modeler
from path_manager import PathManager

# %%
# Setting for experiment
# TODO: duration の設定などの追加
# TODO: 混合を使うかの設定
if __name__ == "__main__":
    print("04_simulation.py")
    # %%
    setting = PathManager.setting_df()
    setting["model"] = "GM"
    # setting["model"] = ""
    setting_dicts = [d.to_dict() for _, d in setting.iterrows()]

    results_list = []
    for condition_i, setting_i in enumerate(setting_dicts):
        # DataLoad
        train_x, train_y, test_x, test_token = PathManager\
            .load_data(**setting_i)
        # TODO: Data Augmentation(train, test)
        # train は duration の調整+幅の調整(特徴量を作る段階じゃん...)
        # test は duration の要因化
        # Modeling
        model = Modeler(**setting_i)
        # TODO: Model のパラメータチェック(bell curve, tmat, duration)
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
# 非mixtureだと rle&pitch:pitch_delta が微妙. そもそも L_H で LHH がでない
# mixture にすると rle&pitch:pitch_delta が LHH を出すし、L_ も妥当になる
results_df.head()
def combine_lambda(x): return '{}&{}'.format(x.encoding, x.feature)


results_df["conditions"] = results_df.apply(combine_lambda, axis=1)
exp_cond = list(set(results_df.conditions))
exp_cond.sort()


for exp_cond_i in exp_cond:
    results_df_i = results_df.query(f"conditions == '{exp_cond_i}'")
    print(exp_cond_i)
    gg = (
        ggplot(results_df_i, aes(x='res'))
        + facet_grid("area~pitch")
        + geom_histogram(binwidth=0.5)  # specify the binwidth
        + theme(axis_text_x=element_text(rotation=90, hjust=1))
    )
    print(gg)

# %%

# %%

# %%
