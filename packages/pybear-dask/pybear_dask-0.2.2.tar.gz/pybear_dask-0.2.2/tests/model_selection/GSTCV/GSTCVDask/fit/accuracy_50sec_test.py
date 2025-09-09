# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV as sk_GSCV
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression as sk_LogisticRegression
from sklearn.metrics import make_scorer

from pybear_dask.model_selection.GSTCV._GSTCVDask.GSTCVDask import GSTCVDask



class TestFitAccuracy:

    # this module tests the equality of GSTCVDask's cv_results_
    # with 0.5 threshold against sklearn GSCV cv_results_.


    # fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    # create tight log init params to supersede session params for this test.
    # need tighter params on logistic to get GSTCV & sk_GSCV to agree.
    @staticmethod
    @pytest.fixture()
    def special_sk_log_init_params():
        return {
            'C': 1e-3,
            'tol': 1e-9,  # need 1e-9 here to pass est accuracy tests
            'max_iter': 100000,  # need 100000 here to pass est accuracy tests
            'fit_intercept': False,
            'solver': 'lbfgs'
        }


    @staticmethod
    @pytest.fixture
    def special_sk_est_log(special_sk_log_init_params):
        return sk_LogisticRegression(**special_sk_log_init_params)


    @staticmethod
    @pytest.fixture()
    def special_sk_GSCV_est_log_one_scorer_prefit(
        sk_gscv_init_params, special_sk_est_log, param_grid_sk_log
    ):

        _sk_GSCV = sk_GSCV(**sk_gscv_init_params)
        _sk_GSCV.set_params(
            estimator=special_sk_est_log,
            param_grid=param_grid_sk_log,
            refit=False
        )
        return _sk_GSCV


    @staticmethod
    @pytest.fixture(scope='module')
    def _cv_iter(X_da, y_da):
        # using sklearn modules to stay off dask_ml. but sklearn uses
        # StratifiedKfold to do splits and GSTCVDask uses dask_ml KFold.
        # so to get equal comparison, use the same splits in GSTCVDask
        # and sk_GSCV by passing the same splits to both.
        # convert to tuple because it needs to be used 2X (iter will spend)
        return list(tuple(
            KFold(
                n_splits=2,    # only using 2 here to save some time
                shuffle=False
            ).split(X_da.compute(), y_da.compute())
        ))

    # END fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @pytest.mark.parametrize('_param_grid',
        (
             [
                 {'C': [1e-1, 1e0], 'fit_intercept': [True, False]}
             ],
             [
                 {'C': [1]},
                 {'C': [1], 'fit_intercept': [False], 'solver': ['lbfgs']}
             ],
        )
    )
    @pytest.mark.parametrize('_return_train_score', (True, False))
    def test_accuracy_vs_sk_gscv(
            self, _param_grid, _cv_iter, standard_error_score, standard_WIP_scorer,
            standard_cache_cv, standard_iid, _return_train_score, X_da, y_da,
            special_sk_est_log, special_sk_GSCV_est_log_one_scorer_prefit,
            # _client  # 25_05_06 indifferent to client
    ):

        # using sklearn modules to stay off dask_ml. but sklearn uses
        # StratifiedKfold to do splits and GSTCVDask uses dask_ml KFold.
        # so to get equal comparison, use the same splits in GSTCVDask
        # and sk_GSCV by passing the same splits to both.

        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        TestCls = GSTCVDask(
            estimator=special_sk_est_log,
            param_grid=_param_grid,
            thresholds=0.5,
            cv=_cv_iter,
            error_score=standard_error_score,
            refit=False,
            verbose=0,
            scoring=standard_WIP_scorer,
            cache_cv=standard_cache_cv,
            iid=standard_iid,
            return_train_score=_return_train_score
        )

        TestCls.fit(X_da, y_da)

        gstcv_cv_results = pd.DataFrame(TestCls.cv_results_)
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        out_sk_gscv = special_sk_GSCV_est_log_one_scorer_prefit
        out_sk_gscv.set_params(
            param_grid=_param_grid,
            cv=_cv_iter,
            scoring={k: make_scorer(v) for k, v in standard_WIP_scorer.items()},
            return_train_score=_return_train_score
        )

        out_sk_gscv.fit(X_da.compute(), y_da.compute())

        sk_cv_results = pd.DataFrame(out_sk_gscv.cv_results_)
        # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


        assert gstcv_cv_results.shape[0] == sk_cv_results.shape[0], \
            f"different rows in cv_results_"

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _gscv_cols = sk_cv_results.columns.to_numpy()
        _drop = [i for i in gstcv_cv_results.columns if 'threshold' in i]
        _gstcv_cols = gstcv_cv_results.drop(columns=_drop).columns.to_numpy()
        del _drop
        assert np.array_equiv(_gscv_cols, _gstcv_cols), \
            f'columns not equal / out of order'
        del _gscv_cols, _gstcv_cols
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        for column in gstcv_cv_results:

            if 'threshold' in column:
                assert (gstcv_cv_results[column] == 0.5).all()
                continue  # notice continuing here
            elif 'time' in column:
                assert (gstcv_cv_results[column] >= 0).all()
                assert (sk_cv_results[column] >= 0).all()
                continue  # notice continuing here
            else:
                assert column in sk_cv_results, \
                    f'\033[91mcolumn {column} not in!\033[0m'
                # notice we flow thru to more tests

            MASK = np.logical_not(gstcv_cv_results[column].isna())

            try:
                _gstcv_out = gstcv_cv_results[column][MASK]
                _gstcv_out = _gstcv_out.to_numpy(dtype=np.float64)
                _sk_out = sk_cv_results[column][MASK]
                _sk_out = _sk_out.to_numpy(dtype=np.float64)
                raise UnicodeError
            except UnicodeError:
                # check floats
                assert np.allclose(_gstcv_out, _sk_out, atol=0.00001)
            except:
                # check param columns
                assert np.array_equiv(
                    gstcv_cv_results[column][MASK].to_numpy(),
                    sk_cv_results[column][MASK].to_numpy()
                )



