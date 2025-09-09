# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import dask.array as da
from dask import compute
from sklearn.model_selection import KFold as sk_KFold
from dask_ml.model_selection import KFold as dask_KFold

from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._estimator_fit_params_helper \
    import _estimator_fit_params_helper



class TestEstimatorFitParamsHelper:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture
    def good_dask_fit_params(_rows):
        return {
            'sample_weight': da.random.uniform(0, 1, _rows),
            'fake_sample_weight': da.random.uniform(0, 1, _rows // 2),
            'made_up_param_1':  'something_else',
            'made_up_param_2': False,
            'some_other_param_1': {'abc': 123}
        }


    @staticmethod
    @pytest.fixture
    def good_sk_fit_params(good_dask_fit_params):
        # use dask fit params to make sk, this is needed because the
        # vectors in fit params must be equal
        __ = {}
        for param, value in good_dask_fit_params.items():
            try:
                __[param] = value.compute()
            except:
                __[param] = value

        return __


    @staticmethod
    @pytest.fixture
    def good_sk_kfold(standard_cv_int, X_da, y_da):
        return list(sk_KFold(n_splits=standard_cv_int).split(X_da, y_da))


    @staticmethod
    @pytest.fixture
    def good_dask_kfold(standard_cv_int, X_da, y_da):
        return list(dask_KFold(n_splits=standard_cv_int).split(X_da, y_da))


    @staticmethod
    @pytest.fixture
    def exp_dask_helper_output(_rows, good_dask_fit_params, good_dask_kfold):

        dask_helper = {}

        for idx, (train_idxs, test_idxs) in enumerate(good_dask_kfold):
            dask_helper[idx] = {}
            for k, v in good_dask_fit_params.items():
                try:
                    iter(v)
                    if isinstance(v, (dict, str)):
                        raise Exception
                    if len(v) != _rows:
                        raise Exception
                    dask_helper[idx][k] = v.copy()[train_idxs]
                except:
                    dask_helper[idx][k] = v

        return dask_helper


    @staticmethod
    @pytest.fixture
    def exp_sk_helper_output(_rows, good_sk_fit_params, good_sk_kfold):

        dask_helper = {}

        for idx, (train_idxs, test_idxs) in enumerate(good_sk_kfold):
            dask_helper[idx] = {}
            for k, v in good_sk_fit_params.items():
                try:
                    iter(v)
                    if isinstance(v, (dict, str)):
                        raise Exception
                    if len(v) != _rows:
                        raise Exception
                    dask_helper[idx][k] = v.copy()[train_idxs]
                except:
                    dask_helper[idx][k] = v

        return dask_helper

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *



    # test validation of args ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('bad_data_len',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), {'a': 1}, min,
         lambda x: x)
    )
    def test_data_len_rejects_not_pos_int(
        self, bad_data_len, good_sk_fit_params, good_dask_fit_params,
        good_sk_kfold, good_dask_kfold
    ):

        with pytest.raises(TypeError):
            _estimator_fit_params_helper(
                bad_data_len, good_sk_fit_params, good_sk_kfold
            )

        with pytest.raises(TypeError):
            _estimator_fit_params_helper(
                bad_data_len, good_dask_fit_params, good_dask_kfold
            )


    @pytest.mark.parametrize('bad_fit_params',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), min, lambda x: x)
    )
    def test_fit_params_rejects_not_dict(
        self, _rows, bad_fit_params, good_sk_kfold, good_dask_kfold
    ):

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, bad_fit_params, good_sk_kfold
            )

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, bad_fit_params, good_dask_kfold
            )



    @pytest.mark.parametrize('bad_kfold',
        (-3.14, -1, 0, True, None, 'junk', [0,1], (1,2), {'a': 1}, min,
         lambda x: x)
    )
    def test_kfold_rejects_not_list_of_tuples(
        self, _rows, good_sk_fit_params, good_dask_fit_params, bad_kfold
    ):

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, good_sk_fit_params, bad_kfold
            )

        with pytest.raises(AssertionError):
            _estimator_fit_params_helper(
                _rows, good_dask_fit_params, bad_kfold
            )

    # END test validation of args ** * ** * ** * ** * ** * ** * ** * ** *




    # test accuracy ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @pytest.mark.parametrize('kfold_type', ('dask', 'sklearn'))
    @pytest.mark.parametrize('fit_params_type', ('dask', 'sklearn'))
    def test_accuracy(
        self, good_sk_fit_params, good_sk_kfold, exp_sk_helper_output,
        _rows, good_dask_fit_params, good_dask_kfold, exp_dask_helper_output,
        kfold_type, fit_params_type
    ):

        if fit_params_type=='dask':
            _fit_params = good_dask_fit_params
            _exp_helper_output = exp_dask_helper_output
        elif fit_params_type=='sklearn':
            _fit_params = good_sk_fit_params
            _exp_helper_output = exp_sk_helper_output

        if kfold_type=='dask':
            _kfold = good_dask_kfold
        elif kfold_type=='sklearn':
            _kfold = good_sk_kfold

        out = _estimator_fit_params_helper(_rows, _fit_params, _kfold)


        for f_idx, exp_fold_fit_param_dict in _exp_helper_output.items():

            for param, exp_value in exp_fold_fit_param_dict.items():
                _act = out[f_idx][param]
                if isinstance(exp_value, da.core.Array):
                    assert isinstance(_act, da.core.Array)
                    assert compute(len(_act))[0] < _rows
                    assert np.array_equiv(_act.compute(), exp_value.compute())
                elif isinstance(exp_value, np.ndarray):
                    assert isinstance(out[f_idx][param], np.ndarray)
                    assert len(_act) < _rows
                    assert len(exp_value) < _rows
                    assert np.array_equiv(_act, exp_value)
                else:
                    assert _act == exp_value


    def test_accuracy_empty(self, _rows, good_dask_kfold):

        out = _estimator_fit_params_helper(
            _rows,
            {},
            good_dask_kfold
        )

        assert np.array_equiv(list(out), list(range(len(good_dask_kfold))))

        for idx, fit_params in out.items():
            assert fit_params == {}


