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

from pybear.preprocessing import MinCountTransformer as MCT


# dask_ml is sending a dummy 1D row vector of zeros to MCT transform,
# apparently it is some kind of primer? this would cause MCT to need to
# accept min_samples=1. this also would cause MCT to raise when 0 is in
# delete_instr, because deleting the one row would be delete of all rows.
# as of 25_06_17 no longer designing for wrap with dask_ml wrappers.


pytest.skip(reason=f'25_06_17 no longer design for dask_ml', allow_module_level=True)



# TEST DASK Incremental + ParallelPostFit == ONE BIG fit_transform()
class TestDaskIncrementalParallelPostFit:


    @pytest.mark.parametrize('x_format', ('da_array', 'ddf'))
    @pytest.mark.parametrize('y_format', ('da_vector', None))
    @pytest.mark.parametrize('row_chunk', (10, 20)) # less than conftest _shape[0]
    @pytest.mark.parametrize('wrappings', ('incr', 'ppf', 'both', 'none'))
    def test_fit_and_transform_accuracy(
        self, wrappings, _X_factory, y_np, _columns, x_format, y_format,
        _kwargs, _shape, row_chunk
    ):

        # faster without client, dont even test it again

        # build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # repeat until _X_factory makes an X that wont be wiped out
        _ctr = 0
        while True:
            _X_np = _X_factory(
                _dupl=None, _has_nan=False, _dtype='int', _shape=_shape
            )

            try:
                MCT(**_kwargs).fit_transform(_X_np)
                break
            except:
                _ctr += 1
                if _ctr == 200:
                    raise Exception(f'failed to make good X in {_ctr} tries')
                continue
        # END build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        if wrappings == 'incr':
            _test_cls = Incremental(MCT(**_kwargs))
        elif wrappings == 'ppf':
            _test_cls = ParallelPostFit(MCT(**_kwargs))
        elif wrappings == 'both':
            _test_cls = ParallelPostFit(Incremental(MCT(**_kwargs)))
        elif wrappings == 'none':
            _test_cls = MCT(**_kwargs)
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
            # dask objects into MCT
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
            MCT(**_kwargs).fit_transform(_X_np)
        ), f"wrapped output != unwrapped output"





