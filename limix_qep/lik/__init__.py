import numpy as np

class Bernoulli(object):
    def assert_outcome(self, y):
        y = np.asarray(y)
        if not np.all(np.logical_or(y == 0.0, y == 1.0)):
            raise Exception("Wrong outcome value(s): %s." % str(y))

class Binomial(object):
    # ntrials can be either a scalar, in which case it is assumed
    # that all samples have the same number of trials, and a
    # array, in which case a different number of trials can be specified
    # for each sample.
    def __init__(self, ntrials, nsamples=None):
        if np.isscalar(ntrials):
            assert nsamples is not None, ("You need to set" +\
                                          " the number of samples.")
            ntrials = np.full(nsamples, ntrials, dtype=float)
        self._ntrials = np.asarray(ntrials, float)
        assert len(self._ntrials.shape) == 1
        if nsamples is not None:
            assert self._ntrials.shape[0] == nsamples

    @property
    def ntrials(self):
        return self._ntrials

    def assert_outcome(self, y):
        ntrials = self.ntrials
        y = np.asarray(y)
        for i in xrange(self.ntrials.shape[0]):
            if y[i] > ntrials[i] or y[i] < 0 or int(y[i]) != y[i]:
                raise Exception("Wrong outcome value: %s." % str(y[i]))
