# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import dask.array as da
import dask.dataframe as ddf


# this module tests score for handling y.
# any X validation is handled by the estimator.



class TestDaskScore_Y_Validation:


    @pytest.mark.parametrize('junk_y',
        (-1, 0, 1, 3.14, True, False, None, 'trash', min, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_y(
        self, X_np, junk_y, dask_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_da
    ):

        # this is raised by estimator, let it raise whatever
        with pytest.raises(Exception):
            dask_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_da.fit(X_np, junk_y)


    @pytest.mark.parametrize('_scoring',
        (['accuracy'], ['accuracy', 'balanced_accuracy']))
    @pytest.mark.parametrize('_y_container', ('da', 'df'))
    @pytest.mark.parametrize('_y_state', ('bad_features', 'bad_data'))
    def test_scoring(
        self, X_da, _scoring, _y_container, _y_state, _rows, _cols, COLUMNS,
        _client,
        dask_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_da,
        dask_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_da
    ):

        if _scoring == ['accuracy']:
            dask_GSTCV = dask_GSTCV_est_log_one_scorer_postfit_refit_str_fit_on_da
        elif _scoring == ['accuracy', 'balanced_accuracy']:
            dask_GSTCV = dask_GSTCV_est_log_two_scorers_postfit_refit_str_fit_on_da

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
            # his should raise by _val_y for not in [0,1]
            with pytest.raises(ValueError):
                getattr(dask_GSTCV, 'score')(X_da, y_dask)
        elif _y_state == 'bad_features':
            # this is raised by GSTCV in _val_y
            with pytest.raises(ValueError):
                getattr(dask_GSTCV, 'score')(X_da, y_dask)



