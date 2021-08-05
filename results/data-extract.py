#%%
import glob
import pandas as pd
import base64
from ffmpy import FFmpeg

N_TRIALS = 4
csv_path = "illusory-vowel-keihan.csv"
results = pd.read_csv(csv_path)
# run_id ベースで分析をすればかぶらない
#%%
# run_id -- subject id
columns = ["run_id", "trial_type", "response"]
subject_id_trial = "survey-html-form"
run_id_subj_id = results[columns].query(f"trial_type == '{subject_id_trial}'")
run_id_subj_id["response"] = run_id_subj_id.response.apply(lambda res: int(eval(res)["subject_id"]))
assert len(run_id_subj_id) == N_TRIALS
#%%
# run_id -- wav
columns = ["run_id", "type", "task", "item_id", "read", "audio_data"]
audio_results = results[columns].query("task == 'production'").query("type=='target'")
#%%
for i, row in audio_results.iterrows():
    file_base = str(row["run_id"])+"_"+row["item_id"]
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
# %%
