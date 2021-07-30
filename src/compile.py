#%%
import pandas as pd

production_list_df = pd.read_csv("./production_list.csv")[["task", "item_id", "read", "type"]]
production_list_str = ",".join([str(dict(row_i)) for _, row_i in production_list_df.iterrows()])

with open("production_list.js", mode='w') as f:
    f.write(f"var production_list = [{production_list_str}]")