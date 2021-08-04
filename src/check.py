#%%
# assert if the content under output/ is as expected
# assert if 
import pandas as pd
import numpy as np

samples = ['eSupo.wav', 'eSpo.wav'] # 音がでかすぎるので変更
csv_path, target_cols = "./list/axb_list.csv", ["a","x","b"]

check_list_stimulus = list(pd.read_csv(csv_path)[target_cols].to_numpy().flatten())
check_list_stimulus = set(check_list_stimulus + samples)

preload_path = "./list/list_audio_preload.csv"
check_list_preload = set(pd.read_csv(preload_path).to_numpy().flatten())

ideal = check_list_stimulus - check_list_preload
actual = check_list_preload - check_list_stimulus
print(f"{ideal} -> {actual}")

# assert len(check_list_stimulus - check_list_preload)==0
# assert len(check_list_preload - check_list_stimulus)==0