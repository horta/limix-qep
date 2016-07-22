from __future__ import absolute_import
from __future__ import division

import logging

import numpy as np

from limix_math.linalg import sum2diag
from limix_math.dist.beta import isf as bisf

from hcache import cached
from .dists import Joint


from limix_qep.special.nbinom_moms import moments_array3, init

from numpy import var as variance

from .base import EP

_NALPHAS0 = 100
_ALPHAS0 = bisf(0.55, 2., 1.-
                np.linspace(0, 1, _NALPHAS0+1, endpoint=False)[1:])
_NALPHAS1 = 30
_ALPHAS1_EPS = 1e-3


# K = \sigma_g^2 Q (S + \delta I) Q.T
class OverdispersionEP(EP):
    """
    .. math::
        K = v Q S Q.T
        M = svd_U svd_S svd_V.T
        \\tilde \\beta = svd_S^{1/2} svd_V.T \\beta
        \\tilde M = svd_U svd_S^{1/2} \\tilde \\beta
        m = M \\beta
        m = \\tilde M \\tilde \\beta
    """
    def __init__(self, M, Q, S, QSQt=None):
        super(OverdispersionEP, self).__init__(M, Q, S, QSQt=QSQt)
        self._logger = logging.getLogger(__name__)

        self._joint = Joint(Q, S)
        self._delta = None

    def initialize_hyperparams(self):
        raise NotImplementedError

    @cached
    def K(self):
        """:math:`K = v (Q S Q.T + \\delta I)`"""
        return sum2diag(self.var * self._QSQt(), self.var * self.delta)

    ############################################################################
    ############################################################################
    ######################## Getters and setters ###############################
    ############################################################################
    ############################################################################
    @property
    def delta(self):
        if self._delta is None:
            self.initialize_hyperparams()
        return self._delta

    @delta.setter
    def delta(self, value):
        self.clear_cache('_lml_components')
        self.clear_cache('_L')
        self.clear_cache('_update')
        self._delta = max(value, 1e-7)

    def h2(self):
        var = self.var
        varc = variance(self.m())
        delta = self.delta
        return var / (var + var*delta + varc + 1.)

    def h2tovar(self, h2):
        varc = variance(self.m())
        delta = self.delta
        return h2 * (1 + varc) / (1 - h2 - delta*h2)

    def _best_alpha0(self, alpha1, opt_beta):
        min_cost = np.inf
        alpha0_min = None
        for i in range(_NALPHAS0):
            (var, delta) = _alphas2hyperparams(_ALPHAS0[i], alpha1)

            self.var = var
            self.delta = delta
            self._update()
            if opt_beta:
                self._optimize_beta()

            cost = -self.lml()
            if cost < min_cost:
                min_cost = cost
                alpha0_min = _ALPHAS0[i]

        return (alpha0_min, min_cost)

    def _create_fun_cost_both(self, opt_beta):
        def fun_cost(alpha1):
            (_, min_cost) = self._best_alpha0(alpha1, opt_beta)
            return min_cost
        return fun_cost

    ############################################################################
    ############################################################################
    ############## Key but Intermediary Matrix Definitions #####################
    ############################################################################
    ############################################################################
    @cached
    def _A0(self):
        """:math:`v \\delta \\mathrm I`"""
        return self.var * self.delta

    @cached
    def _A1(self):
        """:math:`(v \\delta \\mathrm I + \\tilde{\\mathrm T}^{-1})^{-1}`"""
        ttau = self._sites.tau
        return ttau / (self.var * self.delta * ttau + 1)

    @cached
    def _A2(self):
        """:math:`\\tilde{\\mathrm T}^{-1} \\mathrm A_1`"""
        ttau = self._sites.tau
        return 1 / (self.var * self.delta * ttau + 1)


def _alphas2hyperparams(alpha0, alpha1):
    a0 = 1-alpha0
    a1 = 1-alpha1
    var = alpha0 / (a0*a1)
    delta = (a0 * alpha1)/alpha0
    return (var, delta)
