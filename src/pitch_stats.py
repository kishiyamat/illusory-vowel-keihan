# %%
import parselmouth
import pandas as pd
import glob
from pathlib import Path

# duration for reference
# duration for reference
mora_dict = dict(
    esko="reference",
    etsto="reference",
    esuko="distractor",
    etsuto="distractor"
)
mora_dict.items()
# %%
# %%
results = []
for k, v in mora_dict.items():
    wavs = glob.glob(f"audio/output/{k}*.wav")
    for wav in wavs:
        res_i = dict(
            phoneme=[k],
            s_type=[v],
            fname=[Path(wav).name],
            duration=[max(parselmouth.Sound(wav).xs())],
        )
        results.append(pd.DataFrame(res_i))
results = pd.concat(results, ignore_index=True)
# %%
results.groupby(["s_type"]).mean()*1000
# %%
results.groupby(["s_type"]).std()*1000
