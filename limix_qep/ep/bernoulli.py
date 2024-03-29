from __future__ import absolute_import

import logging

from numpy import log
from numpy import clip
from numpy import sqrt
from numpy import exp
from numpy import full
from numpy import asarray
from numpy import isfinite
from numpy import set_printoptions
from numpy import all as all_
from numpy.linalg import lstsq

from limix_math import issingleton
from limix_math.special import normal_logcdf
from limix_math.special import normal_logpdf

from lim.genetics import FastLMM
from lim.genetics.heritability import bern2lat_correction

from .base import EP


class BernoulliPredictor(object):

    def __init__(self, mean, cov):
        self._mean = mean
        self._cov = cov

    def normal_logpdf(self, y):
        ind = 2 * y - 1
        return normal_logcdf(ind * self._mean / sqrt(1 + self._cov))

    def pdf(self, y):
        return exp(self.normal_logpdf(y))

# K = \sigma_g^2 Q S Q.T


class BernoulliEP(EP):

    def __init__(self, y, M, Q0, Q1, S0, Q0S0Q0t=None):
        super(BernoulliEP, self).__init__(M, Q0, S0, Q0S0Q0t=Q0S0Q0t)
        self._logger = logging.getLogger(__name__)

        y = asarray(y, float)
        self._y = y

        if issingleton(y):
            raise ValueError("The phenotype array has a single unique value" +
                             " only.")

        if not all_(isfinite(y)):
            raise ValueError("There are non-finite numbers in phenotype.")

        assert y.shape[0] == M.shape[0], 'Number of individuals mismatch.'
        assert y.shape[0] == Q0.shape[0], 'Number of individuals mismatch.'
        assert y.shape[0] == Q1.shape[0], 'Number of individuals mismatch.'

        self._y11 = 2. * self._y - 1.0
        self._Q1 = Q1

    def initialize_hyperparams(self):
        from scipy.stats import norm
        y = self._y
        ratio = sum(y) / float(len(y))
        latent_mean = norm(0, 1).isf(1 - ratio)
        latent = y / y.std()
        latent = latent - latent.mean() + latent_mean

        Q0 = self._Q0
        Q1 = self._Q1
        covariates = self._M
        flmm = FastLMM(full(len(y), latent), covariates,
                       QS=[[Q0, Q1], [self._S0]])
        flmm.learn()
        gv = flmm.genetic_variance
        nv = flmm.environmental_variance
        h2 = gv / (gv + nv)
        h2 = bern2lat_correction(h2, ratio, ratio)
        h2 = clip(h2, 0.01, 0.9)

        mean = flmm.mean
        self._v = h2 / (1 - h2)
        self._tbeta = lstsq(self._tM, full(len(y), mean))[0]

    def predict(self, m, var, covar):
        (mu, sig2) = self._posterior_normal(m, var, covar)
        return BernoulliPredictor(mu, sig2)

    def _tilted_params(self):
        b = sqrt(self._cavs.tau**2 + self._cavs.tau)
        lb = log(b)
        c = self._y11 * self._cavs.eta / b
        lcdf = self._loghz
        lcdf[:] = normal_logcdf(c)
        lpdf = normal_logpdf(c)
        self._hmu[:] = self._cavs.eta / self._cavs.tau \
            + self._y11 * exp(lpdf - (lcdf + lb))

        self._hvar[:] = 1. / self._cavs.tau\
            - exp(lpdf - (lcdf + 2 * lb)) * (c + exp(lpdf - lcdf))

    # \hat z
    def _compute_hz(self):
        b = sqrt(self._cavs.tau**2 + self._cavs.tau)
        c = self._y11 * self._cavs.eta / b
        self._loghz[:] = normal_logcdf(c)

    def __str__(self):
        set_printoptions(precision=3, threshold=10)
        s = """
Phenotype definition:
  y_l = Indicator(f_l > 0), where f_l is the latent phenotype of the l-th
        individual.

Input data:
  y: {y}""".format(y=bytes(self._y))
        set_printoptions(edgeitems=3, infstr='inf', linewidth=75, nanstr='nan',
                         precision=8, suppress=False, threshold=1000,
                         formatter=None)
        return s + "\n" + super(BernoulliEP, self).__str__()
