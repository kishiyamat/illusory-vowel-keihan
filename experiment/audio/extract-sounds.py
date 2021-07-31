# %%
from parselmouth import TextGrid
import parselmouth
import tgt as textgrid  # tgt is ambiguous: target--textgrid

# https://readthedocs.org/projects/parselmouth/downloads/pdf/latest/
# %%
# 前提:
# wavとtextgridは同じ名前で保存されている
pid = 1
target = f"{pid}-edit"
ignore = "silent"
tier_name = "silences"
tgt_path = f'{target}.TextGrid'
output_dir = "output"

tier = textgrid.io.read_textgrid(tgt_path).get_tier_by_name(tier_name)
tgt_intervals = filter(lambda t: t.text != ignore, tier)
snd = parselmouth.Sound(f"{target}.wav")
for interval in tgt_intervals:
    snd_part = snd.extract_part(from_time=interval.start_time,
                                to_time=interval.end_time,
                                preserve_times=False)
    snd_part.save(f"{output_dir}/" + interval.text + f"-{pid}.wav", 'WAV')

# TODO: assert if the content under output/ is as expected
# TODO: do the same thing for retakes