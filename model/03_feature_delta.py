# %%
import matplotlib.pyplot as plt
import numpy as np

from path_manager import PathManager
from preprocessor import Preprocessor

# %%
# Data Load
setting_i = {
    "area": "tokyo",  # 東京居住歴 (異なるパターンへの許容度)
    "span_tokyo": 10,  # 東京居住歴 (異なるパターンへの許容度)
    "span_kinki": 0,  # 近畿居住歴 (異なるパターンへの許容度)
    "encoding": "base",
    "feature": "base:delta",
    "pid": 0,
}

# ((pitch, intensity), ...)
# train data は12(6x2)しかない
train_x, train_y, _, _ = PathManager.load_data(**setting_i)
pid_i = setting_i["pid"]
for i in range(12):
    data_i = i

    train_x_i, train_y_i = train_x[data_i], train_y[data_i]
    print(train_x_i.shape)
    print(train_y_i.shape)
    print(train_y_i)

    pitch_i = train_x_i[0, :]
    plt.plot(pitch_i)
    plt.show()
    pitch_i[pitch_i == 0] = "nan"
    # 1モーラ200ms程度で、データ1つあたり25ms
    # 7だと175, 8だと200ms, 10だと250ms
    compare_with = list(range(7, 11))
    delta_pitch = Preprocessor.delta_ensemble(pitch_i, width_list=compare_with)
    delta_pitch[np.isnan(delta_pitch)] = 0  # 表示のため
    plt.plot(delta_pitch)
    plt.show()
# %%
