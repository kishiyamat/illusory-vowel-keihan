#%%
import pandas as pd

def csv2json(var_name, target_cols, dir="."):
    """
    var_name: csvはjs内での変数名にする。変数名かぶりが発生しない。
    target_cols: csvの中からjsonに吐き出す列を指定する。
    """
    csv_df = pd.read_csv(f"{dir}/{var_name}.csv")[target_cols]
    list_json = ",".join([str(dict(row_i)) for _, row_i in csv_df.iterrows()])

    with open(f"{dir}/{var_name}.js", mode='w') as f:
        f.write(f"var {var_name} = [{list_json}];\n")

save_dir = "list"
var_name = "production_list"
target_cols = ["task", "item_id", "type", "read"]
csv2json(var_name, target_cols, save_dir)

var_name = "perception_list"
target_cols = ["task", "item_id","type","a","x","b","correct","item_a","item_x","item_b"]
csv2json(var_name, target_cols, save_dir)
# %%
import glob 
var_name = "list_audio_preload"
sample = list(glob.glob("audio/sample/*.wav"))
ouput = list(glob.glob("audio/output/*.wav"))

results = sample + ouput
results = list(map(lambda s: "'" + s.split("/")[-1] + "'", results))
results = ",".join(results)

with open(f"{save_dir}/{var_name}.js", mode='w') as f:
    f.write(f"var {var_name} = [{results}];\n")

# チェック用にcsvも生成
with open(f"{save_dir}/{var_name}.csv", mode='w') as f:
    for_csv = results.replace(",","\n").replace("'", "")
    f.write(f"{var_name}\n{for_csv }\n")
# %%
