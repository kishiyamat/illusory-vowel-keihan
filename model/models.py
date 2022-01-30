import numpy as np
from hsmmlearn.emissions import AbstractEmissions
from hsmmlearn.hsmm import HSMMModel
from sklearn.mixture import GaussianMixture
from typing import List

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin


class GaussianMultivariateMixtureModel(AbstractEmissions, BaseEstimator, TransformerMixin):
    def __init__(self, n_components: int):
        self.n_components = n_components
        self.le = LabelEncoder()
        self.gmms = []
        self.imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

    def fit(self, X, y):
        """
        """
        X = self.imputer.fit_transform(X)
        y = self.le.fit_transform(y)
        for lab in self.le.classes_:
            self.gmms.append(GaussianMixture(n_components=self.n_components)
                             .fit(X[lab == y, :]))
        return self

    def predict(self, X):
        # こちらはうまく動いている
        X = self.imputer.fit_transform(X)
        return self.le.inverse_transform(self.likelihood(X).argmax(axis=0))

    def likelihood(self, X):
        """
        X: (n_sample, n_features)
        """
        X = self.imputer.fit_transform(X)
        likelihood_arr = np.vstack(  # log-lik->likelihood
            [np.exp(gmm.score_samples(X)) for gmm in self.gmms])
        if likelihood_arr.shape != (len(self.le.classes_), X.shape[0]):
            raise ValueError
        return likelihood_arr


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
