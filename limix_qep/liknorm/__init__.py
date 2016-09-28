from . import _liknorm_ffi
from numba import cffi_support as _cffi_support
_cffi_support.register_module(_liknorm_ffi)

from numpy import ndarray


def ptr(a):
    if isinstance(a, ndarray):
        return _liknorm_ffi.ffi.cast("double *", a.ctypes.data)
    return a


class LikNormMoments(object):

    def __init__(self, nintervals, likname):
        super(LikNormMoments, self).__init__()

        liknames = dict(zip(["binomial", "bernoulli", "poisson", "gamma",
                             "exponential", "geometric"], range(6)))
        _liknorm_ffi.lib.initialize(nintervals)

        self._likname_id = liknames[likname]

    def compute(self, y, aphi, eta, tau, log_zeroth, mean, variance):
        _liknorm_ffi.lib.moments(self._likname_id, ptr(y), ptr(aphi),
                                 ptr(tau), ptr(eta), len(tau), ptr(log_zeroth),
                                 ptr(mean), ptr(variance))

    def destroy(self):
        _liknorm_ffi.lib.destroy()