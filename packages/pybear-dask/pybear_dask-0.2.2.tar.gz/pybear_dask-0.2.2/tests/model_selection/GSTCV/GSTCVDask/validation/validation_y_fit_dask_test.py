# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest
from copy import deepcopy
import dask.array as da
import dask.dataframe as ddf


# this module tests fit for handling y.
# any X validation is handled by the estimator.



class TestDaskFit_Y_Validation:


    @pytest.mark.parametrize('junk_y',
        (-1, 0, 1, 3.14, True, False, None, 'trash', min, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_y(
        self, X_da, junk_y, dask_GSTCV_est_log_one_scorer_prefit, _client
    ):

        # this is raised by estimator, let it raise whatever
        with pytest.raises(Exception):
            dask_GSTCV_est_log_one_scorer_prefit.fit(X_da, junk_y)


    @pytest.mark.parametrize('_y_container', ('da', 'df'))
    @pytest.mark.parametrize('_y_state', ('bad_data', 'bad_features'))
    def test_y(
        self, _y_container, _y_state, X_da, _rows, _cols,
        COLUMNS, dask_GSTCV_est_log_one_scorer_prefit, #_client
    ):

        # need to make a new instance of the prefit GSTCV, because the fitting
        # tests alter its state along the way, and it is a session fixture
        shallow_params = \
            deepcopy(dask_GSTCV_est_log_one_scorer_prefit.get_params(deep=False))
        deep_params = \
            deepcopy(dask_GSTCV_est_log_one_scorer_prefit.get_params(deep=True))

        dask_GSTCV = type(dask_GSTCV_est_log_one_scorer_prefit)(**shallow_params)
        dask_GSTCV.set_params(**deep_params)

        # y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        if _y_state == 'bad_data':
            y_dask = da.random.choice(list('abcd'), (_rows, 1), replace=True)
        elif _y_state == 'bad_features':
            y_dask = da.random.randint(0, 2, (_rows, 2))
        else:
            raise Exception

        if _y_container == 'df':
            y_dask = ddf.from_dask_array(y_dask)
        # END y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


        if _y_state == 'bad_data':
            # GSTCVDask _val_y should raise for not in [0,1]
            with pytest.raises(ValueError):
                getattr(dask_GSTCV, 'fit')(X_da, y_dask)
        elif _y_state == 'bad_features':
            # GSTCVDask _val_y should raise for not in [0,1]
            with pytest.raises(ValueError):
                getattr(dask_GSTCV, 'fit')(X_da, y_dask)




