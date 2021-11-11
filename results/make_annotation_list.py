# %%
import glob
from pathlib import Path

lines = []
for path_i in glob.glob("wav/*.wav"):
    filename = Path(path_i).with_suffix("").stem
    assert not "." in filename
    assert not "," in filename
    assert not "\n" in filename
    # ユーザー名が _ を含んでも-1なら問題ない
    item_id = filename.split("_")[-1]
    for order in range(1, 4):
        lines.append(",".join([filename, item_id, str(order), "NA"]))
lines.sort()
# %%
with open("_devoicing_annotation.csv", 'w') as file:  # -> wav
    lines.insert(0, ",".join(["filename", "item_id", "order", "devoiced"]))
    file.write("\n".join(lines))
# %%
