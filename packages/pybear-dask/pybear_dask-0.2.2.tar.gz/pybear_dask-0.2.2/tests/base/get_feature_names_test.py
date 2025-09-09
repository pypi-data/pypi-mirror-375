# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import dask.array as da
import dask.dataframe as ddf

from pybear.base._get_feature_names import get_feature_names



class TestGetFeatureNamesDask:

    # this pybear-dask test module only tests getting feature names from
    # dask containers. for more notes, see the pybear test module for
    # _get_feature_names


    @staticmethod
    @pytest.fixture(scope='module')
    def _shape():
        return (37, 13)


    @staticmethod
    @pytest.fixture(scope='module')
    def _columns(_master_columns, _shape):
        return _master_columns.copy()[:_shape[1]].astype(object)


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_np(_X_factory, _shape):
        return _X_factory(
            _dupl=None,
            _has_nan=False,
            _format='np',
            _dtype='flt',
            _columns=None,
            _constants=None,
            _zeros=0,
            _shape=_shape
        )


    @pytest.mark.parametrize('_format', ('dask_array', 'dask_series', 'dask_ddf'))
    @pytest.mark.parametrize('_columns_is_passed', (True, False))
    def test_accuracy(
        self, _shape, _columns, _X_np, _format, _columns_is_passed
    ):

        if _format == 'dask_array':
            _X_wip = da.from_array(_X_np, chunks=_shape)
        elif _format in ['dask_ddf', 'dask_series']:
            _X_wip = ddf.from_array(
                arr=_X_np,
                columns=_columns if _columns_is_passed else None,
                chunksize=_shape
            )
            if _format == 'dask_series':
                _X_wip = _X_wip.iloc[:, 0].squeeze()
        else:
            raise Exception

        if _format in ['dask_series', 'dask_ddf'] and not _columns_is_passed:
            with pytest.warns():
                # this warns for non-str feature names
                # (the default header when 'columns=' is not passed)
                out = get_feature_names(_X_wip)
        else:
            out = get_feature_names(_X_wip)

        if not _columns_is_passed:
            assert out is None
        elif _columns_is_passed:
            if _format in ['dask_series', 'dask_ddf']:
                assert isinstance(out, np.ndarray)
                assert out.dtype == object
                if _format == 'dask_series':
                    assert np.array_equal(out, _columns[:1])
                else:
                    assert np.array_equal(out, _columns)
            else:
                assert out is None





