# %%
from parselmouth import TextGrid
import parselmouth
import tgt as textgrid  # tgt is ambiguous: target--textgrid

# https://readthedocs.org/projects/parselmouth/downloads/pdf/latest/
# %%
# 前提:
# wavとtextgridは同じ名前で保存されている
ignore = "silent"
tier_name = "silences"
output_dir = "output"
#%%
pid = 1
target = f"{pid}-edit"
tgt_path = f'{target}.TextGrid'
tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')

#%%
pid = 1
target = f"{pid}-retake" # 上書きする
tgt_path = f'{target}.TextGrid'
tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')
#%%
pid = 1
target = f"{pid}-retake2" # 上書きする
tgt_path = f'{target}.TextGrid'
tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')
#%%
pid = 2
target = f"{pid}-edit"
tgt_path = f'{target}.TextGrid'
tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')

#%%
pid = 3
target = f"{pid}-edit"
tgt_path = f'{target}.TextGrid'
tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')

# TODO: do the same thing for retakes
# %%
