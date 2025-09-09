# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from dask_ml.model_selection import KFold as dask_KFold

from pybear.model_selection.GSTCV._GSTCVMixin._validation._cv import _val_cv



class TestValCV:


    @pytest.mark.parametrize('_n_splits', (3,4,5))
    @pytest.mark.parametrize('_container', (tuple, list, np.ndarray))
    def test_accepts_good_dask_iter(self, _n_splits, _container, X_da, y_da):

        good_iter = dask_KFold(n_splits=_n_splits).split(X_da, y_da)

        if _container in [tuple, list]:
            good_iter2 = _container(map(
                tuple,
                dask_KFold(n_splits=_n_splits).split(X_da,y_da)
            ))
        elif _container is np.ndarray:
            good_iter2 = np.array(
                list(map(
                    tuple,
                    dask_KFold(n_splits=_n_splits).split(X_da,y_da)
                )),
                dtype=object
            )
        else:
            raise Exception


        assert _val_cv(good_iter) is None
        assert _val_cv(good_iter2) is None



