#%%
import pandas as pd

def csv2json(var_name, target_cols):
    """
    var_name: csvはjs内での変数名にする。変数名かぶりが発生しない。
    target_cols: csvの中からjsonに吐き出す列を指定する。
    """
    csv_df = pd.read_csv(f"{var_name}.csv")[target_cols]
    list_json = ",".join([str(dict(row_i)) for _, row_i in csv_df.iterrows()])

    with open(f"{var_name}.js", mode='w') as f:
        f.write(f"var {var_name} = [{list_json}];")

var_name = "production_list"
target_cols = ["task", "item_id", "type", "read"]
csv2json(var_name, target_cols)

var_name = "perception_list"
target_cols = ["task", "item_id","type","speaker_1","speaker_2","speaker_3","correct","item_a","item_x","item_b"]
csv2json(var_name, target_cols)
# %%