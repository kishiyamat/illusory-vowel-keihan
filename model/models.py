import numpy as np
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from sklearn.mixture import GaussianMixture
from typing import List


class GaussianMixtureEmissions(AbstractEmissions):

    dtype = np.float64

    def __init__(self, gms: List[GaussianMixture]):
        self.gms = gms
        self.K = len(gms)

    def likelihood(self, obs):
        """
        obs: (n_samples, n_dimensions)
        """
        obs = np.squeeze(obs)
        # https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html
        n_samples = obs.shape[0]
        # loglikelihood じゃなくて likelihood だから np.exp が必要
        likelihood_arr = np.vstack(
            [np.exp(gm.score_samples(obs)) for gm in self.gms])
        if likelihood_arr.shape != (self.K, n_samples):
            raise ValueError
        return likelihood_arr


class GaussianMixtureHSMM(HSMMModel):
    """ A HSMM class with discrete multinomial emissions.
    """

    def __init__(self, gm_list, durations, tmat,
                 startprob=None, support_cutoff=100):
        emissions = GaussianMixtureEmissions(gm_list)
        super(GaussianMixtureHSMM, self).__init__(
            emissions, durations, tmat,
            startprob=startprob, support_cutoff=support_cutoff
        )
