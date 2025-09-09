# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import dask.array as da
import dask.dataframe as ddf

from dask_ml.wrappers import (
    Incremental,
    ParallelPostFit
)

from pybear.preprocessing import InterceptManager as IM



# TEST DASK Incremental + ParallelPostFit == ONE BIG fit_transform()
class TestDaskIncrementalParallelPostFit:


    @pytest.mark.parametrize('x_format', ['da_array', 'ddf'])
    @pytest.mark.parametrize('y_format', ['da_vector', None])
    @pytest.mark.parametrize('row_chunk', (2, 5)) # less than conftest _shape[0]
    @pytest.mark.parametrize('wrappings', ('incr', 'ppf', 'both', 'none'))
    def test_fit_and_transform_accuracy(
        self, wrappings, _X_factory, y_np, _columns, x_format, y_format,
        _kwargs, _shape, row_chunk
    ):

        # faster without client, dont even test it again

        _X_np = _X_factory(
            _constants={0:1, 1:2}, _has_nan=False, _dtype='flt', _shape=_shape
        )

        if wrappings == 'incr':
            _test_cls = Incremental(IM(**_kwargs))
        elif wrappings == 'ppf':
            _test_cls = ParallelPostFit(IM(**_kwargs))
        elif wrappings == 'both':
            _test_cls = ParallelPostFit(Incremental(IM(**_kwargs)))
        elif wrappings == 'none':
            _test_cls = IM(**_kwargs)
        else:
            raise Exception


        _X = da.from_array(_X_np).rechunk((row_chunk, _shape[1]))
        if x_format == 'da_array':
            pass
        elif x_format == 'ddf':
            _X = ddf.from_dask_array(_X, columns=_columns)
        else:
            raise Exception

        if y_format is None:
            _y = None
            _y_np = None
        elif y_format == 'da_vector':
            _y = da.from_array(y_np).rechunk((row_chunk,))
            _y_np = y_np.copy()
        else:
            raise Exception

        _was_fitted = False
        # incr covers fit() so should accept all objects for fits

        # vvv fit vvv

        if wrappings in ['none', 'ppf']:
            # without any wrappers, should except for trying to put
            # dask objects into IM
            with pytest.raises(TypeError):
                _test_cls.partial_fit(_X, _y)
            pytest.skip(reason=f"cannot do more tests if not fit")
        elif wrappings in ['incr', 'both']:
            # dask object being fit by chunks into Incremental wrapper
            _test_cls.partial_fit(_X, _y)
        else:
            raise Exception

        # ^^^ END fit ^^^

        # vvv transform vvv

        # always TypeError when try to pass y to wrapper's transform
        with pytest.raises(TypeError):
            _test_cls.transform(_X, _y)

        # always transforms with just X
        TRFM_X = _test_cls.transform(_X)

        if x_format == 'da_array':
            assert isinstance(TRFM_X, da.core.Array)
        elif x_format == 'ddf':
            assert isinstance(TRFM_X, ddf.DataFrame)

        # ^^^ transform ^^^

        # CONVERT TO NP ARRAY FOR COMPARISON AGAINST REF fit_trfm()
        TRFM_X = TRFM_X.compute()

        if isinstance(TRFM_X, pd.DataFrame):
            TRFM_X = TRFM_X.to_numpy()

        assert isinstance(TRFM_X, np.ndarray)
        # END CONVERT TO NP ARRAY FOR COMPARISON AGAINST REF fit_trfm()


        assert np.array_equal(
            TRFM_X,
            IM(**_kwargs).fit_transform(_X_np, _y_np)
        ), f"wrapped output != unwrapped output"





