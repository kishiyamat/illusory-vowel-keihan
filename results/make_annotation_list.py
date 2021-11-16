# %%
# アノテーションに使うcsvの雛形を作成
import glob
from pathlib import Path

lines = []
for path_i in glob.glob("wav/*.wav"):
    filename = path_i[4:-4]  # wav/ と .wav を省く
    assert not "," in filename
    assert not "\n" in filename
    # ユーザー名が _ を含んでも-1なら問題ない
    item_id = filename.split("_")[-1]
    for order in range(1, 4):
        lines.append(",".join([filename, item_id, str(order), "NA"]))
lines.sort()
lines
# %%
with open("_devoicing_annotation.csv", 'w') as file:  # -> wav
    lines.insert(0, ",".join(["filename", "item_id", "order", "voiced"]))
    file.write("\n".join(lines))
# %%
