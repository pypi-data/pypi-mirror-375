# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numbers

import numpy as np
import dask.array as da

from sklearn.linear_model import LogisticRegression as sk_logistic
from sklearn.linear_model import SGDClassifier as sk_SGDClassifier

from pybear.base.mixins._GetParamsMixin import GetParamsMixin
from pybear.base.mixins._SetParamsMixin import SetParamsMixin



@pytest.fixture(scope='session')
def _shape():
    # must have enough rows to avoid error in StratifiedKFold for more
    # splits than number of members in each class in y.
    return (int(np.random.randint(20, 100)), int(np.random.randint(1, 20)))


@pytest.fixture(scope='session')
def X_da(_shape):
    return da.random.randint(0, 10, _shape)


@pytest.fixture(scope='session')
def y_da(_shape):
    return da.random.randint(0, 2, (_shape[0], ))


@pytest.fixture(scope='session')
def mock_estimator():


    class MockEstimator(GetParamsMixin, SetParamsMixin):

        def __init__(
            self,
            param_a:numbers.Real = 5,
            param_b:numbers.Real = np.pi
        ) -> None:

            self.param_a = param_a
            self.param_b = param_b


        def partial_fit(self, X):
            if isinstance(X, da.core.Array):
                _min_dim = min(X.shape)
                X += float(self.param_a)
                _square_matrix = X[:_min_dim, :_min_dim]
            else:
                X = np.array(X)
                _min_dim = min(X.shape)
                X += float(self.param_a)
                _square_matrix = X[:_min_dim, :_min_dim]

            _square_matrix -= self.param_b

            if hasattr(self, '_square_matrix'):
                self._square_matrix += _square_matrix
            else:
                self._square_matrix = _square_matrix

            return self


        def fit(self, X, y):

            if isinstance(X, da.core.Array):
                X = X.astype(np.float64)
                _min_dim = min(X.shape)
                X += float(self.param_a)
                _square_matrix = X[:_min_dim, :_min_dim]
            else:
                X = np.array(X).astype(np.float64)
                _min_dim = min(X.shape)
                X += float(self.param_a)
                _square_matrix = X[:_min_dim, :_min_dim]

            _square_matrix -= self.param_b

            self._square_matrix = _square_matrix

            return self


        def predict_proba(self, X):

            _rows = X.shape[0]

            if isinstance(X, da.core.Array):
                return da.random.uniform(0, 1, (_rows, 2))
            else:
                return np.random.uniform(0, 1, (_rows, 2))


        def predict(self, X):
            return (self.predict_proba(X)[:-1] >= 0.5).astype(np.uint8)


        def score(self, X, y):   # needs two args to satisify sklearn
            return self._square_matrix[0].sum() / self._square_matrix.sum()


    return MockEstimator()


@pytest.fixture(scope='session')
def mock_estimator_params():
    # using a mock estimator to significantly reduce fit() time
    return {
        'param_a': [np.logspace(-5, 5, 3), 3, 'soft_float'],
        'param_b': [[1, 2], 2, 'fixed_integer']
    }


@pytest.fixture(scope='session')
def dask_estimator_1():
    # use sklearn to stay off you-know-who
    return sk_logistic(
        penalty='l2',
        dual=False,
        tol=0.0001,
        C=1e-5,
        fit_intercept=False,
        intercept_scaling=1.0,
        class_weight=None,
        random_state=None,
        solver='lbfgs',
        max_iter=100,
        multi_class='deprecated',
        verbose=0,
        warm_start=False,
        n_jobs=None,
        # solver_kwargs=None
    )


@pytest.fixture(scope='session')
def dask_params_1():
    return {
        'C': [np.logspace(-5, 5, 3), 3, 'soft_float'],
        'solver': [['lbfgs', 'saga'], 2, 'fixed_string']
    }


@pytest.fixture(scope='session')
def dask_estimator_2():
    # has partial_fit method
    # some dask GSCVs (like Incremental) need estimator with partial_fit
    return sk_SGDClassifier(
        loss='hinge',
        penalty='l2',
        # alpha=0.0001,
        l1_ratio=0.15,
        # fit_intercept=True,
        max_iter=1000,
        tol=0.001,
        shuffle=True,
        verbose=0,
        epsilon=0.1,
        n_jobs=None,
        random_state=None,
        # learning_rate='optimal',
        eta0=0.1,
        power_t=0.5,
        early_stopping=False,
        validation_fraction=0.1,
        n_iter_no_change=5,
        class_weight=None,
        warm_start=False,
        average=False
    )


@pytest.fixture(scope='session')
def dask_params_2():
    return {
        'alpha': [np.logspace(-5, 5, 3), [3,3], 'soft_float'],
        'learning_rate': [['constant', 'optimal'], 2, 'fixed_string'],
    }




