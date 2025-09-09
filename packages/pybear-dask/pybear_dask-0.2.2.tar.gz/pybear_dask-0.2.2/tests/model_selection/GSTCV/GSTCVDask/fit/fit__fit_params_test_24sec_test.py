# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import dask.array as da



class TestCoreFit_FitParams:


    @staticmethod
    @pytest.fixture()
    def special_GSTCVDask(dask_GSTCV_est_log_one_scorer_prefit):
        # create a copy of the session fixture
        # do not mutate the session fixture!
        __ = dask_GSTCV_est_log_one_scorer_prefit
        return type(__)(**__.get_params(deep=False))


    def test_rejects_sample_weight_too_short(
        self, special_GSTCVDask, X_da, y_da, _rows#, _client
    ):

        short_sample_weight = da.random.uniform(0, 1, _rows//2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            special_GSTCVDask.fit(X_da, y_da, sample_weight=short_sample_weight)


    def test_rejects_sample_weight_too_long(
        self, special_GSTCVDask, X_da, y_da, _rows#, _client
    ):

        long_sample_weight = da.random.uniform(0, 1, _rows*2)

        # ValueError should raise inside _parallel_fit ('error_score'=='raise')
        with pytest.raises(ValueError):
            special_GSTCVDask.fit(X_da, y_da, sample_weight=long_sample_weight)


    def test_correct_sample_weight_works(
        self, special_GSTCVDask, dask_est_log, X_da, y_da, _rows, _client
    ):

        # with Client is faster

        correct_sample_weight = da.random.uniform(0, 1, _rows)

        assert isinstance(
            special_GSTCVDask.fit(X_da, y_da, sample_weight=correct_sample_weight),
            type(special_GSTCVDask)
        )








