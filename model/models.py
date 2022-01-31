import numpy as np
from hsmmlearn.emissions import AbstractEmissions
from sklearn.mixture import GaussianMixture

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
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
        X = self.imputer.fit_transform(X)
        return self.le.inverse_transform(self.likelihood(X).argmax(axis=0))

    def likelihood(self, X):
        """
        X: (n_sample, n_features)
        """
        X = self.imputer.fit_transform(X)
        likelihood_arr = np.vstack(  # log-lik->likelihood
            [np.exp(gmm.score_samples(X)) for gmm in self.gmms])
        likelihood_arr += 0.001  # likelihood に0があると尤度のpathが途絶える
        likelihood_arr /= likelihood_arr.sum(axis=0)  # predict_proba
        if likelihood_arr.shape != (len(self.le.classes_), X.shape[0]):
            raise ValueError
        return likelihood_arr
