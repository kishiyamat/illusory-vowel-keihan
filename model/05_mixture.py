# %%
import numpy as np
from modeler import Modeler
from path_manager import PathManager
from sklearn.mixture import GaussianMixture
# %%
X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
print(X.shape)
gm = GaussianMixture(n_components=2, random_state=0).fit(X)
gm.means_
# %%
gm.predict([[0, 0], [12, 3]])
# %%
setting = PathManager.setting_df()
setting_dicts = [d.to_dict() for _, d in setting.iterrows()]
setting_i = setting_dicts[5]
X, y, test_x, test_token = PathManager.load_data(**setting_i)
#%%
test_x[0]
# %%
K = list(set(np.concatenate(y)))  # ordered list
K.sort()
X_by_K = Modeler._X_by_K(X, y, K)
# %%
X_by_K0 = X_by_K[K[0]].T
gm = GaussianMixture(n_components=2, random_state=0).fit(X_by_K0)
# gm.means_
gm.get_params()
# %%
print(gm.means_)
print(gm.covariances_)  # 一つのラベルに2つの状態がある。
# %%
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel

class GaussianMixtureEmissions(AbstractEmissions):

    dtype = np.float64
        
    def __init__(self, gms):
        self.gms = gms

    def likelihood(self, obs):
        obs = np.squeeze(obs)
        # TODO: build in some check for the shape of the likelihoods, otherwise
        # this will silently fail and give the wrong results.
        # 状態のインデックス順の分布を当てはめていく
        # https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html
        # (n_cat, len_obs) なのかな？
        # exp したらできた...? loglikelihood じゃなくて likelihood だから？
        ll = np.vstack([np.exp(gm.score_samples(obs)) for gm in gms] )
        print(ll.shape)
        print(ll)
        # score_samples
        return ll

class GaussianMixtureHSMM(HSMMModel):
    """ A HSMM class with discrete multinomial emissions.
    """

    def __init__(self, gms, durations, tmat,
                 startprob=None, support_cutoff=100):
        emissions = GaussianMixtureEmissions(gms)
        super(GaussianMixtureHSMM, self).__init__(
            emissions, durations, tmat,
            startprob=startprob, support_cutoff=support_cutoff
        )

# %%

gms = []
for k in K:
    X_by_k = X_by_K[k].T
    # この　n_components も本当は手動で決める。
    gms.append(GaussianMixture(n_components=2, random_state=0).fit(X_by_k))

startprob, tmat = Modeler._startprob_tmat(y, K)
#%%
duration_by_K = Modeler._duration_by_K(y, K)
dur_std_mean = np.mean([np.std(duration_by_K[k]) for k in K])
Modeler._dur_std_mean = dur_std_mean
durations = np.concatenate([v for _, v in duration_by_K.items()])
dur_max = np.max(durations)  # 24のbinがあるこれを1/4のサイズにする。
# dur_max に std のint分は上限を追加する
durations = np.array(
    [Modeler._duration_dist(duration_by_K[k], dur_max+int(dur_std_mean), 4) for k in K]
)
#%%
gm_hsmm = GaussianMixtureHSMM(
    GaussianMixtureEmissions(gms), durations, tmat, startprob
)
#%%
tmat
startprob
durations
# %%
gm_hsmm.decode(test_x[1])
# %%
for K_i , gms_i in zip(K, gms):
    print(K_i)
    print(gms_i.means_)
# %%
