#%%
import pandas as pd

with open('_experiment.js', "r") as f:
    lines = f.read()

assert lines.count("prod_list_to_be_replaced") == 1

# prod_list_to_be_replaced => list
prod_list_df = pd.read_csv("./list/item_production - list.csv")[["type", "item_id", "read"]]
prod_list_str = ",".join([str(dict(row_i)) for _, row_i in prod_list_df.iterrows()])
lines = lines.replace("prod_list_to_be_replaced", prod_list_str)

with open("experiment.js", mode='w') as f:
    f.write(lines)

assert lines.count("to_be_replaced") == 0  # 変換漏れが無いことを保証
#%%
# if __name__=="__main__":
#     print("hi")
#     print("hi")
