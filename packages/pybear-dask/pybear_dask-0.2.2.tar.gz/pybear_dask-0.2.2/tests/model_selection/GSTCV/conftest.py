# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy.typing as npt

import time
from uuid import uuid4

import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl
import dask.array as da
import dask.dataframe as ddf

from sklearn.preprocessing import StandardScaler as sk_StandardScaler

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression

from sklearn.metrics import (
    precision_score,
    recall_score,
    accuracy_score,
    balanced_accuracy_score
)

from pybear_dask.model_selection.GSTCV._GSTCVDask.GSTCVDask import \
    GSTCVDask as dask_GSTCV



# data objects ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
@pytest.fixture(scope='session')
def _rows():
    # must have at least 5 rows for dask chunk //5 division
    return int(np.random.randint(5, 200))


@pytest.fixture(scope='session')
def _cols():
    return int(np.random.randint(1, 10))


@pytest.fixture(scope='session')
def X_np(_rows, _cols):
    np.random.seed(19)
    return np.random.randint(0, 10, (_rows, _cols))


@pytest.fixture(scope='session')
def X_da(_rows, _cols):
    da.random.seed(19)
    return da.random.randint(
        0, 10, (_rows, _cols)
    ).rechunk((int(_rows//5), _cols)).astype(np.float64)


@pytest.fixture(scope='session')
def COLUMNS(_cols):
    return [str(uuid4())[:4] for _ in range(_cols)]


@pytest.fixture(scope='session')
def X_pd(X_np, COLUMNS):
    return pd.DataFrame(data=X_np, columns=COLUMNS)


@pytest.fixture(scope='session')
def X_ddf(X_da, COLUMNS):
    return ddf.from_dask_array(X_da, columns=COLUMNS)


@pytest.fixture(scope='session')
def y_np(_rows):
    np.random.seed(19)
    return np.random.randint(0, 2, (_rows,))


@pytest.fixture(scope='session')
def y_da(_rows):
    np.random.seed(19)
    return da.random.randint(0, 2, (_rows,)).rechunk((int(_rows/10),))


@pytest.fixture(scope='session')
def y_pd(y_np):
    return pd.DataFrame(data=y_np, columns=['y'])


@pytest.fixture(scope='session')
def y_ddf(y_da):
    return ddf.from_dask_array(y_da, columns=['y'])

# END data objects ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# WIP init param objects ** * ** * ** * ** * ** * ** * ** * ** * ** * **

@pytest.fixture(scope='session')
def standard_WIP_scorer():
    return {
        'precision': precision_score,
        'recall': recall_score,
        'accuracy': accuracy_score,
        'balanced_accuracy': balanced_accuracy_score
    }


# END WIP init param objects ** * ** * ** * ** * ** * ** * ** * ** * **


# estimator init params ** * ** * ** * ** * ** * ** * ** * ** * ** * **

@pytest.fixture(scope='session')
def sk_log_init_params():
    return {
        'C':1e-8,
        'tol': 1e-1,
        'max_iter': 1,
        'fit_intercept': False,
        'solver': 'lbfgs'
    }


@pytest.fixture(scope='session')
def dask_log_init_params():

    return {
        'C':1e-8,
        'tol': 1e-1,
        'max_iter': 2,
        'fit_intercept': False,
        'solver': 'lbfgs',
        'random_state': 69
    }

# END estimator init params ** * ** * ** * ** * ** * ** * ** * ** * ** *

# transformers / estimators ** * ** * ** * ** * ** * ** * ** * ** * ** *
@pytest.fixture(scope='session')
def sk_standard_scaler():
    return sk_StandardScaler(with_mean=True, with_std=True)


@pytest.fixture(scope='session')
def sk_est_log(sk_log_init_params):
    return sk_LogisticRegression(**sk_log_init_params)


@pytest.fixture(scope='session')
def dask_est_log(dask_log_init_params):
    # 25_04_29 converted this to sklearn for speed and risk mitigation
    return sk_LogisticRegression(**dask_log_init_params)
# END transformers / estimators ** * ** * ** * ** * ** * ** * ** * ** *


# grid search params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
@pytest.fixture(scope='session')
def param_grid_sk_log():
    return {'C': [1e-4, 1e-5]}


@pytest.fixture(scope='session')
def param_grid_dask_log():
    return {'C': [1e-4, 1e-5]}


@pytest.fixture(scope='session')
def standard_thresholds():
    return np.linspace(0.4, 0.6, 3)


@pytest.fixture(scope='session')
def standard_cv_int():
    return 4


@pytest.fixture(scope='session')
def standard_refit():
    return False


@pytest.fixture(scope='session')
def one_scorer():
    return 'accuracy'


@pytest.fixture(scope='session')
def two_scorers():
    return ['accuracy', 'balanced_accuracy']


@pytest.fixture(scope='session')
def standard_error_score():
    return 'raise'


@pytest.fixture(scope='session')
def standard_n_jobs():
    return 1


@pytest.fixture(scope='session')
def standard_cache_cv():
    return True


@pytest.fixture(scope='session')
def standard_iid():
    return True
# END grid search params ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# gs(t)cv init params ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

@pytest.fixture(scope='session')
def sk_gscv_init_params(
    sk_est_log, param_grid_sk_log, one_scorer, standard_n_jobs,
    standard_refit, standard_cv_int, standard_error_score
):

    return {
        'estimator': sk_est_log,
        'param_grid': param_grid_sk_log,
        'scoring': one_scorer,
        'n_jobs': standard_n_jobs,
        'refit': standard_refit,
        'cv': standard_cv_int,
        'verbose': 0,
        'pre_dispatch': '2*n_jobs',
        'error_score': standard_error_score,
        'return_train_score': False
    }


@pytest.fixture(scope='session')
def sk_gstcv_init_params(
    sk_est_log, param_grid_sk_log, standard_thresholds, one_scorer,
    standard_n_jobs, standard_refit, standard_cv_int, standard_error_score
):
    return {
        'estimator': sk_est_log,
        'param_grid': param_grid_sk_log,
        'thresholds': standard_thresholds,
        'scoring': one_scorer,
        'n_jobs': standard_n_jobs,
        'pre_dispatch': '2*n_jobs',
        'refit': standard_refit,
        'cv': standard_cv_int,
        'verbose': 0,
        'error_score': standard_error_score,
        'return_train_score': False
    }


@pytest.fixture(scope='session')
def dask_gstcv_init_params(
    dask_est_log, param_grid_dask_log, standard_thresholds, one_scorer,
    standard_n_jobs, standard_refit, standard_cv_int, standard_error_score,
    standard_iid, standard_cache_cv
):
    return {
        'estimator': dask_est_log,
        'param_grid': param_grid_dask_log,
        'thresholds': standard_thresholds,
        'scoring': one_scorer,
        'n_jobs': standard_n_jobs,
        'refit': standard_refit,
        'cv': standard_cv_int,
        'verbose': 0,
        'error_score': standard_error_score,
        'return_train_score': False,
        'iid': standard_iid,
        'cache_cv': standard_cache_cv,
        'scheduler': None
    }

# END gs(t)cv init params ** * ** * ** * ** * ** * ** * ** * ** * ** *


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ESTIMATORS - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * ** *

# gstcv log est one scorer, various refits

@pytest.fixture(scope='session')
def dask_GSTCV_est_log_one_scorer_prefit(dask_gstcv_init_params, _client):

    return dask_GSTCV(**dask_gstcv_init_params)


@pytest.fixture(scope='session')
def dask_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_da(
    dask_gstcv_init_params, one_scorer, X_da, y_da, _client
):

    return dask_GSTCV(
        **dask_gstcv_init_params
    ).set_params(refit=one_scorer).fit(X_da, y_da)

# END gstcv log est one scorer, various refits

# END ESTIMATORS - ONE SCORER ** * ** * ** * ** * ** * ** * ** * ** * **
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *




# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
# ESTIMATORS - TWO SCORERS ** * ** * ** * ** * ** * ** * ** * ** * ** *

# gstcv log est two scorers, various refits
@pytest.fixture(scope='session')
def dask_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_da(
    dask_gstcv_init_params, two_scorers, one_scorer, X_da, y_da, _client
):

    return dask_GSTCV(**dask_gstcv_init_params).set_params(
        scoring=two_scorers, refit=one_scorer
    ).fit(X_da, y_da)

# END gstcv log est two scorers, various refits


# END ESTIMATORS - TWO SCORERS ** * ** * ** * ** * ** * ** * ** * ** *
# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


@pytest.fixture(scope='session')
def _format_helper():


    def foo(
        _base: npt.NDArray | da.core.Array,
        _format: str,
        _dim: int
    ):

        """Cast dummy numpy or dask array to desired container."""

        # _new_X can be X or y in the tests

        if _format in ['da', 'ddf'] and not isinstance(_base, da.core.Array):
            raise ValueError(
                f"must pass '_base' as dask array to cast to 'da' or 'ddf'"
            )

        if _format == 'ss' and _dim == 1:
            raise ValueError(f"cant have 1D scipy sparse")

        if _format == 'py_set' and _dim == 2:
            raise ValueError(f"cant have 2D set")

        if _dim == 1 and len(_base.shape)==1:
            _intrmdt_X = _base.copy()
        elif _dim == 2 and len(_base.shape)==2:
            _intrmdt_X = _base.copy()
        elif _dim == 1 and len(_base.shape)==2:
            _intrmdt_X = _base[:, 0].copy().ravel()
        elif _dim == 2 and len(_base.shape)==1:
            _intrmdt_X = _base.copy().reshape((-1, 1))
        else:
            raise Exception

        if _format == 'py_list':
            if _dim == 1:
                _new_X = list(_intrmdt_X)
            elif _dim == 2:
                _new_X = list(map(list, _intrmdt_X))
        elif _format == 'py_tup':
            if _dim == 1:
                _new_X = tuple(_intrmdt_X)
            elif _dim == 2:
                _new_X = tuple(map(tuple, _intrmdt_X))
        elif _format == 'py_set':
            if _dim == 1:
                _new_X = set(_intrmdt_X)
            elif _dim == 2:
                # should have raised above
                raise Exception
        elif _format == 'np':
            _new_X = _intrmdt_X.copy()
        elif _format == 'pd':
            if _dim == 1:
                _new_X = pd.Series(_intrmdt_X)
            elif _dim == 2:
                _new_X = pd.DataFrame(_intrmdt_X)
        elif _format == 'ss':
            if _dim == 1:
                # should have raised above
                raise Exception
            elif _dim == 2:
                _new_X = ss.csr_array(_intrmdt_X)
        elif _format == 'pl':
            if _dim == 1:
                _new_X = pl.Series(_intrmdt_X)
            elif _dim == 2:
                _new_X = pl.from_numpy(_intrmdt_X)
        elif _format == 'da':
            _new_X = _intrmdt_X.copy()
        elif _format == 'ddf':
            if _dim == 1:
                _new_X = ddf.from_dask_array(_intrmdt_X).squeeze()
            elif _dim == 2:
                _new_X = ddf.from_dask_array(_intrmdt_X)
        else:
            raise ValueError(f"_format_helper invalid format '{_format}'")

        del _intrmdt_X

        return _new_X

    return foo


@pytest.fixture
def _mock_classifier():

    class MockClassifier:

        def __init__(self, command='run'):

            self.command = command
            self.is_fitted = False
            # command can be 'type_error', 'other_error_raise',
            # 'other_error_not_raise', 'run'

        def fit(self, X, y, **fit_params):

            time.sleep(0.5)

            if len(fit_params) and fit_params['kill'] is True:
                raise BrokenPipeError     # an obscure error

            if self.command == 'run':
                self.score_ = self.score(X, y)
                self.is_fitted = True
            elif self.command == 'type_error':
                raise TypeError
            elif self.command == 'other_error_with_raise':
                raise TabError # an obscure error
            elif self.command == 'other_error_not_raise':
                self.score_ = np.nan
                raise TabError # an obscure error

            return self


        def score(self, X, y):

            return float(np.random.uniform(0, 1))


    return MockClassifier



