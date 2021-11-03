import numpy as np
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from sklearn.mixture import GaussianMixture
from typing import List


class MultivariateGaussianMixtureEmissions(AbstractEmissions):

    dtype = np.float64

    def __init__(self, gmms: List[GaussianMixture], n_feature: int):
        self.gmms = gmms
        self.n_feature = n_feature
        self.K = len(gmms)

    def likelihood(self, obs):
        """
        obs: (n_samples, n_dimensions)
        """
        obs = np.squeeze(obs).reshape(-1, self.n_feature)
        # https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html
        n_samples = obs.shape[0]
        # loglikelihood じゃなくて likelihood だから np.exp が必要
        likelihood_arr = np.vstack(
            [np.exp(gmm.score_samples(obs)) for gmm in self.gmms])
        if likelihood_arr.shape != (self.K, n_samples):
            raise ValueError
        return likelihood_arr


class MultivariateGaussianMixtureHSMM(HSMMModel):
    """ A HSMM class with discrete multinomial emissions.
    """
    def __init__(self, gmms, n_feature, durations, tmat,
                 startprob=None, support_cutoff=100):
        emissions = MultivariateGaussianMixtureEmissions(gmms, n_feature)
        super(MultivariateGaussianMixtureHSMM, self).__init__(
            emissions, durations, tmat,
            startprob=startprob, support_cutoff=support_cutoff
        )
