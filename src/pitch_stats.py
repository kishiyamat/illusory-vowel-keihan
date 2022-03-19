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
        results.append(
            pd.DataFrame(
                dict(
                    phoneme=[k],
                    s_type=[v],
                    fname=[Path(wav).name],
                    duration=[max(parselmouth.Sound(wav).xs())],
                )))
results = pd.concat(results, ignore_index=True)
# %%
results
# %%
# %%


print(wavs[0])
snd = parselmouth.Sound(wavs[0])
# xのmaxがsになっているので、これの平均と分散を
# referenceなどごとに見る
max(snd.xs())

# lines.sort()
# lines
# %%
# with open("_devoicing_annotation.csv", 'w') as file:  # -> wav
#     lines.insert(0, ",".join(["filename", "item_id", "order", "voiced"]))
#     file.write("\n".join(lines))
# %%
