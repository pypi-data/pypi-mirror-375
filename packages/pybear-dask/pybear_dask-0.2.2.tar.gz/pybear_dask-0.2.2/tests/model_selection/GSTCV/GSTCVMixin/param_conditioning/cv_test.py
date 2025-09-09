# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import inspect

import numpy as np

from dask_ml.model_selection import KFold as dask_KFold

from pybear.model_selection.GSTCV._GSTCVMixin._param_conditioning._cv \
    import _cond_cv



class TestCondCV:


    def test_accepts_good_dask_iter(self, standard_cv_int, X_da, y_da):

        good_iter = dask_KFold(n_splits=standard_cv_int).split(X_da, y_da)
        # TypeError: cannot pickle 'generator' object
        ref_iter = dask_KFold(n_splits=standard_cv_int).split(X_da, y_da)

        out = _cond_cv(good_iter)
        assert isinstance(out, list)
        assert inspect.isgenerator(good_iter)

        assert inspect.isgenerator(ref_iter)
        ref_iter_as_list = list(ref_iter)
        assert isinstance(ref_iter_as_list, list)

        for idx in range(standard_cv_int):
            for X_y_idx in range(2):
                assert np.array_equiv(
                    out[idx][X_y_idx],
                    ref_iter_as_list[idx][X_y_idx]
                )



