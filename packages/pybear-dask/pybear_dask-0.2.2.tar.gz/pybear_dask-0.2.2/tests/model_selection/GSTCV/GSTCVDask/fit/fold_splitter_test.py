# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import dask.array as da

from pybear_dask.model_selection.GSTCV._GSTCVDask._fit._fold_splitter import \
    _fold_splitter



class TestFoldSplitter:


    @pytest.mark.parametrize('bad_data_object',
        (1, 3.14, True, False, None, 'junk', min, [0,1], (0,1), {0,1},
        {'a':1}, lambda x: x, np.random.randint(0,10,(5,3)))
    )
    def test_rejects_everything_not_dask(self, bad_data_object):
        # this block is in place because of the limited if/elifs that
        # manage the slicing for different containers in _fold_splitter
        with pytest.raises(TypeError):
            _fold_splitter(
                [0,2,4],
                [1,3],
                bad_data_object
            )


    # 25_05_14 no longer explicitly enforcing 1 or 2D
    @pytest.mark.parametrize('bad_data_object',
        (
            da.random.randint(0, 10, (5, 5, 5)),
            da.random.randint(0, 10, (5, 5, 5, 5)),
        )
    )
    def test_rejects_bad_shape(self, bad_data_object):

        # with pytest.raises(AssertionError):
        _fold_splitter(
            [0,2,4],
            [1,3],
            bad_data_object
        )


    @pytest.mark.parametrize('_X1_format', ('da', 'ddf'))
    @pytest.mark.parametrize('_X1_dim', (1, 2))
    @pytest.mark.parametrize('_X2_format', ('da', 'ddf'))
    @pytest.mark.parametrize('_X2_dim', (1, 2))
    def test_accuracy(
        self, _rows, X_da, _format_helper, _X1_format, _X1_dim, _X2_format,
        _X2_dim
    ):










        _X1 = _format_helper(X_da, _X1_format, _X1_dim)
        _X2 = _format_helper(X_da, _X2_format, _X2_dim)

        _helper_mask = da.random.randint(0, 2, (_rows,)).astype(bool)
        mask_train = da.arange(_rows)[_helper_mask]
        mask_test = da.arange(_rows)[da.logical_not(_helper_mask)]
        del _helper_mask

        if _X1_dim == 1:
            _X1_ref_train = X_da[:, 0][mask_train]
            _X1_ref_test = X_da[:, 0][mask_test]
        elif _X1_dim == 2:
            _X1_ref_train = X_da[mask_train]
            _X1_ref_test = X_da[mask_test]
        else:
            raise Exception

        if _X2_dim == 1:
            _X2_ref_train = X_da[:, 0][mask_train]
            _X2_ref_test = X_da[:, 0][mask_test]
        elif _X2_dim == 2:
            _X2_ref_train = X_da[mask_train]
            _X2_ref_test = X_da[mask_test]
        else:
            raise Exception

        out = _fold_splitter(mask_train, mask_test, _X1, _X2)

        assert isinstance(out, tuple)
        assert all(map(isinstance, out, (tuple for i in out)))




        assert type(out[0][0]) == type(_X1)
        if _X1_format == 'da':
            assert np.array_equal(out[0][0].compute(), _X1_ref_train)
        elif _X1_format == 'ddf':
            assert np.array_equal(out[0][0].compute().to_numpy(), _X1_ref_train)
        else:
            raise Exception

        assert type(out[0][1]) == type(_X1)
        if _X1_format == 'da':
            assert np.array_equal(out[0][1].compute(), _X1_ref_test)
        elif _X1_format == 'ddf':
            assert np.array_equal(out[0][1].compute().to_numpy(), _X1_ref_test)
        else:
            raise Exception

        assert type(out[1][0]) == type(_X2)
        if _X2_format == 'da':
            assert np.array_equal(out[1][0].compute(), _X2_ref_train)
        elif _X2_format == 'ddf':
            assert np.array_equal(out[1][0].compute().to_numpy(), _X2_ref_train)
        else:
            raise Exception

        assert type(out[1][1]) == type(_X2)
        if _X2_format == 'da':
            assert np.array_equal(out[1][1].compute(), _X2_ref_test)
        elif _X2_format == 'ddf':
            assert np.array_equal(out[1][1].compute().to_numpy(), _X2_ref_test)
        else:
            raise Exception





