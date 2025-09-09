# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import time
import numpy as np

from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._parallelized_scorer import \
    _parallelized_scorer

from sklearn.metrics import accuracy_score as sk_accuracy_score

from dask_ml.metrics import accuracy_score as dask_accuracy_score

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

    @pytest.mark.parametrize('sk_dask_metrics',
        (
            {'sk_accuracy': sk_accuracy_score},
            {'dask_accuracy': dask_accuracy_score}
        )
    )
    def test_fit_excepted_accuracy(
            self, X_da, y_da, _fit_output_excepted, sk_dask_metrics
    ):

        # 5 folds
        _X_test = X_da[int(0.8 * X_da.shape[0]):, :]
        _y_test = y_da[int(0.8 * y_da.shape[0]):]

        # error_score == np.nan
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT=sk_dask_metrics,
            _THRESHOLDS=np.linspace(0,1,21).tolist(),
            _error_score=np.nan,
            _verbose=10
        )




        assert out_scores.mask.all()
        assert out_times.mask.all()


        # error_score == 0.4 (any arbitrary number)
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_excepted,
            _f_idx=0,
            _SCORER_DICT={
                'accuracy': dask_accuracy_score
            },
            _THRESHOLDS=np.linspace(0,1,21).tolist(),
            _error_score=0.4,
            _verbose=10
        )


        assert round(out_scores.mean(), 8) == 0.4
        assert out_times.mask.all()



    @pytest.mark.parametrize('sk_dask_metrics',
        (
            {'sk_accuracy': sk_accuracy_score},
            {'dask_accuracy': dask_accuracy_score}
        )
    )
    def test_fit_good_accuracy(
        self, X_da, y_da, _fit_output_good, sk_dask_metrics
    ):

        # 5 folds
        _X_test = X_da[int(0.8 * X_da.shape[0]):, :]
        _y_test = y_da[int(0.8 * y_da.shape[0]):]

        # error_score == np.nan
        out_scores, out_times = _parallelized_scorer(
            _X_test,
            _y_test,
            _FIT_OUTPUT_TUPLE=_fit_output_good,
            _f_idx=0,
            _SCORER_DICT=sk_dask_metrics,
            _THRESHOLDS=np.linspace(0, 1, 21).tolist(),
            _error_score=np.nan,
            _verbose=10
        )




        assert out_scores.shape == (21, 1)
        assert not out_scores.mask.any()
        assert out_scores.min() >= 0
        assert out_scores.max() <= 1
        assert out_scores.mean() > 0

        assert out_times.shape == (21, 1)
        assert not out_times.mask.any()
        assert out_times.min() > 0
        assert out_times.mean() > 0




