# %%
import matplotlib.pyplot as plt
import numpy as np

from path_manager import PathManager
from preprocessor import Preprocessor

# %%
if __name__ == "__main__":
    print("03")
    # %%
    train_wav_list, test_wav_list = PathManager.train_test_wav()
    compare_with = list(range(6, 13))

    for wav_i in train_wav_list + test_wav_list:
        print(wav_i)
        pitch_i = np.load(PathManager.data_path("feature", wav_i),
                          allow_pickle=False
                          )[0, :]
        if 'get_ipython' in globals():
            plt.plot(pitch_i)
            plt.show()
        pitch_i[pitch_i == 0] = "nan"  # 計算時にnanを無視させる目的
        pitch_delta = Preprocessor.delta_ensemble(
            pitch_i, width_list=compare_with
        )
        pitch_delta[np.isnan(pitch_delta)] = 0
        if 'get_ipython' in globals():
            plt.plot(pitch_delta)
            plt.show()
        np.save(
            PathManager.data_path("pitch_delta", wav_i),
            pitch_delta.reshape(1, -1), allow_pickle=False
        )
