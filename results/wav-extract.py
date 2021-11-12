# %%
# cognition の結果から wav を抽出
import base64

import pandas as pd
from ffmpy import FFmpeg


def run_id2subj_id(cognition_res) -> dict:
    """
    # TODO: add test
    jsPsychの結果は["run_id", "trial_type", "response"]を含む。
    trial_type の中の "subject_id" はクラウドワークスのユーザー名を含む。
    run_id から subject_id への辞書を作成してマッパーとする

    Args:
        result_df (dict): run_id から subject_id への辞書
    """
    run_id_subj_id = cognition_res[["run_id", "trial_type", "response"]]\
        .query(f"trial_type == 'survey-html-form'")
    subject_id_idx = run_id_subj_id['response'].str.contains("subject_id")
    run_id_subj_id = run_id_subj_id[subject_id_idx]
    run_id_subj_id["response"] = run_id_subj_id.response\
        .apply(lambda res: str(eval(res)["subject_id"]))
    return {r["run_id"]: r["response"] for _idx, r in run_id_subj_id.iterrows()}


# %%
csv_paths = ["csv/illusory-vowel-keihan.csv",
             "csv/illusory-vowel-keihan-cw.csv"]

for csv_path in csv_paths:
    """
    run_id, subj_id, item_id で wav を保存

    1. base64に音声をエンコードしたcsvをread_csv
    1. run_id -> subj_id への辞書を取得
    1. base64 -> webm 変換して保存
    1. webm -> wav 変換して保存
    """
    results = pd.read_csv(csv_path)
    run_id2subj_id_dict = run_id2subj_id(results)
    audio_results = results[["run_id", "type", "task", "item_id", "read", "audio_data"]]\
        .query("task == 'production'").query("type=='target'")
    for _idx, row in audio_results.iterrows():
        # setting
        run_id, item_id = row["run_id"], row["item_id"]
        subj_id = run_id2subj_id_dict[run_id]
        file_base = "_".join(list(map(str, [run_id, subj_id, item_id])))
        webm_file, wav_file = "webm/"+file_base+".webm", "wav/"+file_base+".wav"
        # decode
        decodedData = base64.b64decode(row["audio_data"])  # -> webm
        with open(webm_file, 'wb') as file:  # -> wav
            file.write(decodedData)
        ff = FFmpeg(
            executable='ffmpeg',
            inputs={webm_file: None},
            outputs={wav_file: '-c:a pcm_f32le -y'})  # -y で上書き
        ff.cmd
        ff.run()
