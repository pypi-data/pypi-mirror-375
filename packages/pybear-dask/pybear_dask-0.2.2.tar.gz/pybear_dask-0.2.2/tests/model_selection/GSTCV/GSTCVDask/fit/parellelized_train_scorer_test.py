# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import time
import numpy as np

from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._parallelized_train_scorer \
    import _parallelized_train_scorer

from sklearn.metrics import accuracy_score, balanced_accuracy_score

from sklearn.linear_model import LogisticRegression as sk_logistic



class TestParallelizedScorer:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def _fit_output_excepted():

        # [ClassifierProtocol, fit time, fit excepted]
        return (sk_logistic(), 0.1, True)


    @staticmethod
    @pytest.fixture
    def _fit_output_good(X_da, y_da):

        sk_clf = sk_logistic()

        t0 = time.perf_counter()

        sk_clf.fit(
            X_da[:int(0.8 * X_da.shape[0])],
            y_da[:int(0.8 * y_da.shape[0])]
        )

        tf = time.perf_counter()

        # [ClassifierProtocol, fit time, fit excepted]
        return (sk_clf, tf-t0, False)

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **







    def test_fit_excepted_accuracy(
        self, X_da, y_da, _fit_output_excepted
    ):

        # 5 folds
        _X_train = X_da[:int(0.8 * X_da.shape[0]), :]
        _y_train = y_da[:int(0.8 * y_da.shape[0])]

        # error_score == np.nan
        out_scores = _parallelized_train_scorer(
            _X_train,
            _y_train,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _BEST_THRESHOLDS_BY_SCORER=np.array([45, 55]),
            _error_score=np.nan,
            _verbose=10
        )

        assert out_scores.mask.all()



        # error_score == 0.5 (any arbitrary number)
        out_scores = _parallelized_train_scorer(
            _X_train,
            _y_train,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _BEST_THRESHOLDS_BY_SCORER=np.array([40, 60]),
            _error_score=0.5,
            _verbose=10
        )

        assert out_scores.mean() == 0.5










    def test_fit_good_accuracy(
        self, X_da, y_da, _fit_output_good
    ):

        # 5 folds
        _X_train = X_da[:int(0.8 * X_da.shape[0]), :]
        _y_train = y_da[:int(0.8 * y_da.shape[0])]

        # error_score == np.nan
        out_scores = _parallelized_train_scorer(
            _X_train,
            _y_train,
            _FIT_OUTPUT_TUPLE=_fit_output_good,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': accuracy_score,
                'balanced_accuracy': balanced_accuracy_score
            },
            _BEST_THRESHOLDS_BY_SCORER=np.array([48, 52]),
            _error_score=np.nan,
            _verbose=10
        )

        assert out_scores.shape == (2,)
        assert not out_scores.mask.any()
        assert out_scores.min() >= 0
        assert out_scores.max() <= 1
        assert out_scores.mean() > 0









