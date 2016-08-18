from cffi import FFI
from os.path import join
import ncephes
import limix_math
from glob import glob


def _make():
    ffi = FFI()

    sources = glob(join('limix_qep', 'moments', 'binomial', '*.c'))
    hdrs = glob(join('limix_qep', 'moments', 'binomial', '*.h'))
    incls = [join('limix_qep', 'moments', 'binomial'),
             limix_math.get_include(),
             ncephes.get_include()]

    ffi.set_source('limix_qep.moments._binomial_ffi',
                   '''#include "moments.h"
#include "base.h"''',
                   include_dirs=incls,
                   sources=sources,
                   libraries=['ncprob', 'm'],
                   library_dirs=[limix_math.get_lib(), ncephes.get_lib()],
                   depends=sources + hdrs)

    with open(join('limix_qep', 'moments', 'binomial', 'moments.h'), 'r') as f:
        ffi.cdef(f.read())

    return ffi

binomial = _make()
