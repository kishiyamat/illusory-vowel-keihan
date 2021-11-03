# %%
import numpy as np
from modeler import Modeler
from path_manager import PathManager
from sklearn.mixture import GaussianMixture
from models import GaussianMixtureHSMM, GaussianMixtureEmissions

# %%
setting = PathManager.setting_df()
setting_dicts = [d.to_dict() for _, d in setting.iterrows()]
setting_i = setting_dicts[5]
X, y, test_x, test_token = PathManager.load_data(**setting_i)

K = list(set(np.concatenate(y)))  # ordered list
K.sort()
X_by_K = Modeler._X_by_K(X, y, K)

gms = []
for k in K:
    X_by_k = X_by_K[k].T
    # この　n_components も本当は手動で決める。
    gms.append(GaussianMixture(n_components=2, random_state=0).fit(X_by_k))

startprob, tmat = Modeler._startprob_tmat(y, K)
# %%
duration_by_K = Modeler._duration_by_K(y, K)
dur_std_mean = np.mean([np.std(duration_by_K[k]) for k in K])
Modeler._dur_std_mean = dur_std_mean
durations = np.concatenate([v for _, v in duration_by_K.items()])
dur_max = np.max(durations)  # 24のbinがあるこれを1/4のサイズにする。
# dur_max に std のint分は上限を追加する
durations = np.array(
    [Modeler._duration_dist(duration_by_K[k], dur_max +
                            int(dur_std_mean), 4) for k in K]
)
# %%
len(gms)

# %%
gm_hsmm = GaussianMixtureHSMM(
    gms, durations, tmat, startprob
)
# %%
tmat
startprob
durations
# %%
gm_hsmm.decode(test_x[1])
# %%
for K_i, gms_i in zip(K, gms):
    print(K_i)
    print(gms_i.means_)
# %%
