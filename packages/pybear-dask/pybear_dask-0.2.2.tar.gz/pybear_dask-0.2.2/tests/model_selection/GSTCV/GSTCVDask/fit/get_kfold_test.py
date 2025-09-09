# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import inspect

import numpy as np
import dask.array as da

from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._get_kfold import _get_kfold



class TestGetDaskKFold:


    # X, y must both be da.array
    # AS OF 25_04_28 ONLY DASK ARRAYS CAN BE PASSED TO
    # dask_KFOLD (NOT np, pd.DF, dask.DF)
    # see dask_kfold_input_test in functional_tests folder

    # *** IMPORTANT!!!
    # This function can be called multiple times within a single param
    # grid permutation, first to fit, again to get test score, then again
    # if return_train_score. Therefore, it must return the same indices
    # for each call. The only things that should cause indices to be
    # different are n_splits and the number of rows in X.
    # Since this is dask KFold, there is the wildcard of the 'iid' setting.
    # If iid is False -- meaning the data is known to have some non-random
    # grouping along axis 0 -- via the 'shuffle' argument KFold will
    # generate indices that sample across chunks to randomize the data
    # in the splits. In that case, fix the random_state parameter to make
    # selection repeatable. If iid is True, shuffle is False, random_state
    # can be None, and the splits should be repeatable.


    @pytest.mark.parametrize('_junk_X',
        (-2.7, -1, 0, 1, 2.7, None, 'str', lambda x:x)
    )
    @pytest.mark.parametrize('_junk_y',
        (-2.7, -1, 0, 1, 2.7, None, 'str', lambda x:x)
    )
    def test_X_y_rejects_junk(self, _junk_X, _junk_y):

        # this is raised by dask_ml.KFold, let it raise whatever
        with pytest.raises(Exception):
            list(_get_kfold(
                _junk_X,
                _n_splits=3,
                _iid=True,
                _verbose=0,
                _y=_junk_y
            ))


    @pytest.mark.parametrize(f'junk_n_splits',
        (-1, 0, 1, 3.14, None, min, 'junk', [0, 1], (0, 1), {0, 1},
         {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_n_splits(self, X_da, y_da, junk_n_splits):
        with pytest.raises(AssertionError):
            _get_kfold(
                X_da,
                _n_splits=junk_n_splits,
                _iid=True,
                _verbose=0,
                _y=y_da
            )


    @pytest.mark.parametrize(f'junk_iid',
        (0, 1, 3.14, None, min, 'junk', [0, 1], (0, 1), {0, 1}, {'a': 1},
         lambda x: x)
    )
    def test_rejects_non_bool_iid(self, X_da, y_da, junk_iid):
        with pytest.raises(AssertionError):
            _get_kfold(
                X_da,
                _n_splits=3,
                _iid=junk_iid,
                _verbose=0,
                _y=y_da
            )


    @pytest.mark.parametrize(f'junk_verbose',
        (-1, None, min, 'junk', [0, 1], (0, 1), {0, 1}, {'a': 1}, lambda x: x)
    )
    def test_rejects_junk_verbose(self, X_da, y_da, junk_verbose):
        with pytest.raises(AssertionError):
            _get_kfold(
                X_da,
                _n_splits=3,
                _iid=True,
                _verbose=junk_verbose,
                _y=y_da
            )

    # END validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('_X_dim', (1, 2))
    @pytest.mark.parametrize('_X_format',
        ('da', )
    )
    @pytest.mark.parametrize('_y_dim', (1, 2))
    @pytest.mark.parametrize('_y_format',
        ('da', )
    )
    def test_da_returns_gen_of_das(
        self, X_da, y_da, _format_helper, _X_format, _y_format,
        _X_dim, _y_dim
    ):

        _X = _format_helper(X_da, _X_format, _X_dim)
        _y = _format_helper(y_da, _y_format, _y_dim)

        out1 = _get_kfold(
            X_da,
            _n_splits=3,
            _iid=True,
            _verbose=0,
            _y=y_da
        )

        assert inspect.isgenerator(out1)

        out1_list = list(out1)

        for (train_idxs, test_idxs) in out1:

            assert isinstance(train_idxs, da.core.Array)
            assert isinstance(test_idxs, da.core.Array)

            assert train_idxs.min() >= 0
            assert train_idxs.max() < X_da.shape[0]

            assert test_idxs.min() >= 0
            assert test_idxs.max() < X_da.shape[0]


        # and second call returns same as the first
        out2 = _get_kfold(
            X_da,
            _n_splits=3,
            _iid=True,
            _verbose=0,
            _y=y_da
        )


        for idx, (train_idxs2, test_idxs2) in enumerate(out2):

            assert isinstance(train_idxs2, da.core.Array)
            assert isinstance(test_idxs2, da.core.Array)

            assert train_idxs2.min() >= 0
            assert train_idxs2.max() < X_da.shape[0]

            assert test_idxs2.min() >= 0
            assert test_idxs2.max() < X_da.shape[0]

            assert np.array_equiv(out1_list[idx][0], train_idxs2)
            assert np.array_equiv(out1_list[idx][1], test_idxs2)




