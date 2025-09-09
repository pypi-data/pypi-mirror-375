# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._parallelized_fit import \
    _parallelized_fit



class TestParallelizedFit:


    def test_when_completes_fit(self, _mock_classifier, X_da, y_da):
        # returns fitted est, time, fit_excepted == False
        out_fitted_estimator, out_time, out_fit_excepted = \
            _parallelized_fit(
                int(np.random.randint(0,10)),  # f_idx
                X_da,
                y_da,
                _estimator=_mock_classifier(),
                _grid = {'param_1': True, 'param_2': [3,4,5]},
                _error_score=np.nan
                # **fit_params
            )

        assert isinstance(out_fitted_estimator, _mock_classifier)
        assert isinstance(out_fitted_estimator.score_, float)
        assert out_fitted_estimator.score_ >= 0
        assert out_fitted_estimator.score_ <= 1
        assert isinstance(out_time, float)
        assert out_time > 0.48 # was 0.5, the sleep duration in mock_classifier;
        # this was excepting in github actions for out_time == 0.49ish
        # with windows
        assert out_fit_excepted is False


    def test_other_error_with_raise(self, _mock_classifier, X_da, y_da,):
        # if error_score == 'raise', raise Exception
        with pytest.raises(ValueError):
            _parallelized_fit(
                int(np.random.randint(0,10)),  # f_idx
                X_da,
                y_da,
                _estimator=_mock_classifier(command='other_error_with_raise'),
                _grid = {'param_1': True, 'param_2': [3,4,5]},
                _error_score='raise',  # ineffectual
                # **fit_params
            )


    def test_other_error_not_raise(self, _mock_classifier, X_da, y_da):
        # else warn, fit_excepted = True
        # returns fitted est, time, fit_excepted == False

        out_fitted_estimator, out_time, out_fit_excepted = \
            _parallelized_fit(
                int(np.random.randint(0,10)),  # f_idx
                X_da,
                y_da,
                _estimator=_mock_classifier(command='other_error_not_raise'),
                _grid = {'param_1': True, 'param_2': [3,4,5]},
                _error_score=np.nan,
                # **fit_params
        )

        assert isinstance(out_fitted_estimator, _mock_classifier)
        assert isinstance(out_fitted_estimator.score_, float)
        assert out_fitted_estimator.score_ is np.nan
        assert isinstance(out_time, float)
        assert out_time > 0.48 # was 0.5, the sleep duration in mock_classifier;
        # this was excepting in github actions for out_time == 0.49ish
        # with windows
        assert out_fit_excepted is True


    def test_fit_params(self, _mock_classifier, X_da, y_da):

        with pytest.raises(BrokenPipeError):
            _parallelized_fit(
                int(np.random.randint(0,10)),  # f_idx
                X_da,
                y_da,
                _estimator=_mock_classifier(),
                _grid = {'param_1': True, 'param_2': [3,4,5]},
                _error_score=np.nan,
                kill=True
            )




