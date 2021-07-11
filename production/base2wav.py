#%%
import glob
import pandas as pd
import base64
from ffmpy import FFmpeg

csv_list = glob.glob('**/*.csv', recursive=True)
df_list = [pd.read_csv(csv_str) for csv_str in csv_list]
idx = 0
columns = ["run_id", "type", "item_id", "read", "audio_data"]
df_i = df_list[idx][columns].query("type == 'production'")

#%%
df_list[0]
#%%
for i, row in df_i.iterrows():
    file_base = str(row["run_id"])+"_"+row["item_id"]+"_"+row["read"]
    webm_file = "webm/"+file_base+".webm"
    wav_file = "wav/"+file_base+".wav"
    decodedData = base64.b64decode(row["audio_data"])
    with open(webm_file, 'wb') as file:
       file.write(decodedData)

    # https://takahiro-itazuri.hatenadiary.jp/entry/2017/08/14/211150
    ff = FFmpeg(
        executable = 'ffmpeg',
        inputs={webm_file:None},
        outputs = {wav_file:'-c:a pcm_f32le'})
    ff.cmd
    ff.run()