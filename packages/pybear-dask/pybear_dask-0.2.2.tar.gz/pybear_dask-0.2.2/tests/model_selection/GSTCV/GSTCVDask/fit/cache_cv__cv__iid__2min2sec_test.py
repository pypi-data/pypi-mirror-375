# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from dask_ml.model_selection import KFold as dask_KFold

from pybear_dask.model_selection.GSTCV._GSTCVDask.GSTCVDask import GSTCVDask

# this module tests the dask GSTCV operation of:
# 1) the cache_cv kwarg, proves the equality of cv_results_ when cache_cv
# is True or False.
# 2) the cv kwarg, proves the equality of cv_results_ when cv as int and
# cv as iterable are expected to give identical folds.
# 3) the iid kwarg, proves the equality of cv_results_ on 2 independent
# calls to GSTCV with iid = False on the same data and same cv. iid = True
# cannot be tested for equality with iid = False, because the different
# sampling of train and test will cause different scores.



class TestCVCacheCVIid:


    # indifferent to client
    def test_accuracy(
        self, X_da, y_da, dask_est_log, standard_WIP_scorer#, _client
    ):

        # test equivalent cv as int or iterable give same output
        _cv_int = 3

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # dont use session fixture!
        TestCls1 = GSTCVDask(
            estimator=dask_est_log,
            param_grid=[
                {'C': [1e-5], 'fit_intercept': [True]},
                {'C': [1e-1], 'fit_intercept': [False]}
            ],
            cv=_cv_int,       # <===========
            error_score='raise',
            refit=False,
            verbose=0,
            scoring=standard_WIP_scorer,
            cache_cv=True,     # <===========
            iid=False,         # <===========
            return_train_score=True
        )

        TestCls1.fit(X_da, y_da)

        cv_results_true = pd.DataFrame(TestCls1.cv_results_)
        # drop time columns
        _drop_columns = [c for c in cv_results_true.columns if 'time' in c]
        cv_results_true = cv_results_true.drop(columns=_drop_columns)
        del _drop_columns

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        # must use dask KFold with shuffle off to pass this test
        # dont use session fixture!
        TestCls2 = GSTCVDask(
            estimator=dask_est_log,
            param_grid=[
                {'C': [1e-5], 'fit_intercept': [True]},
                {'C': [1e-1], 'fit_intercept': [False]}
            ],
            cv=dask_KFold(
                n_splits=_cv_int, shuffle=True, random_state=7
            ).split(X_da, y_da), # <===========
            error_score='raise',
            refit=False,
            verbose=0,
            scoring=standard_WIP_scorer,
            cache_cv=False,     # <===========
            iid=False,          # <===========
            return_train_score=True
        )

        TestCls2.fit(X_da, y_da)

        cv_results_false = pd.DataFrame(TestCls2.cv_results_)
        # drop time columns
        _drop_columns = [c for c in cv_results_false.columns if 'time' in c]
        cv_results_false = cv_results_false.drop(columns=_drop_columns)
        del _drop_columns

        # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

        assert np.array_equal(cv_results_true.columns, cv_results_false.columns)

        for _c in cv_results_true.columns:
            assert np.array_equal(cv_results_true[_c], cv_results_false[_c])

        # cv_results_ being equal for both outs proves that comparable
        # cv as int & cv as iterator give same output, cache_cv True and
        # False give the same output, and successive independent calls
        # on the same data & splits with iid = False give the same output



