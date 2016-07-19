from numpy import ones
from numpy import array
from numpy import empty
from numpy import hstack
from numpy import random

from limix_math.linalg import qs_decomposition

from limix_qep.ep import BinomialEP

def test_binomial_lml():

    random.seed(6)
    n = 3
    M = ones((n, 1)) * 1.
    G = array([[1.2, 3.4], [-.1, 1.2], [0.0, .2]])

    (Q, S) = qs_decomposition(G)
    y = array([1., 0., 1.])
    ep = BinomialEP(y, 1, M, hstack(Q), empty((n,0)), hstack(S) + 1.0)
    ep.beta = array([1.])
    ep.sigg2 = 1.
    lml1 = ep.lml()
#     #
#     #     np.random.seed(6)
#     #     n = 3
#     #     M = np.ones((n, 1)) * 1.
#     #     G = np.array([[1.2, 3.4], [-.1, 1.2], [0.0, .2]])
#     #     K = dot(G, G.T) + np.eye(n)*1.0
#     #     (Q, S) = _QS_from_K(K)
#     #     y = np.array([1., 0., 1.])
#     #     ep = EP(y, M, Q, S, outcome_type=Binomial(1, n))
#     #     ep.beta = np.array([1.])
#     #     ep.sigg2 = 1.
#     #     ep.delta = 1e-7
#     #     self.assertAlmostEqual(lml1 - ep.lml(), 0., places=5)
#     #
#     # def test_binomial_optimize(self):
#     #
#     #     seed = 10
#     #     nsamples = 30
#     #     nfeatures = 600
#     #     ntrials = 1
#     #
#     #     M = np.ones((nsamples, 1))
#     #
#     #     (y, G) = create_binomial(nsamples, nfeatures, ntrials, sigg2=1.,
#     #                              delta=0.1, sige2=0.1, seed=seed)
#     #
#     #     (Q, S) = economic_QS(G, 'G')
#     #
#     #     ep = EP(y, M, Q, S, outcome_type=Binomial(1, nsamples))
#     #     ep.optimize(disp=True)
#     #
#     #     self.assertAlmostEqual(ep.lml(), -19.649207220129359, places=5)