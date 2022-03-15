# %%
import glob
from pathlib import Path

lines = []
mora_2 = ["esko", "etsto"]
mora_3 = ["esuko", "etsuto"]

phoneme_i = "esko"
wavs = list(filter(lambda s: phoneme_i in s, glob.glob("audio/output/*.wav")))

import parselmouth

print(wavs[0])
snd = parselmouth.Sound(wavs[0])
max(snd.xs())

# lines.sort()
# lines
# %%
# with open("_devoicing_annotation.csv", 'w') as file:  # -> wav
#     lines.insert(0, ",".join(["filename", "item_id", "order", "voiced"]))
#     file.write("\n".join(lines))
# %%
