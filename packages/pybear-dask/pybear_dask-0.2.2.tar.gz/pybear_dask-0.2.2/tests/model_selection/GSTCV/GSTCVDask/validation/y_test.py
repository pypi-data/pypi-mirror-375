# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import dask.array as da
import dask.dataframe as ddf

from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._y import _val_y



class TestValY:


    @pytest.mark.parametrize('y', (0, True, min, 'junk', lambda x: x))
    def test_rejects_junk_y(self, y):

        with pytest.raises((TypeError, ValueError)):
            _val_y(y)


    def test_rejects_misshapen_y(self, _rows):

        # multicolumn y
        with pytest.raises(ValueError):
            _val_y(da.random.randint(0,2,(_rows,2)))


    def test_rejects_non_binary_y(self, _rows):
        y_dask_bad_array = da.random.choice(list('abcde'), (_rows, 1), replace=True)
        y_dask_bad_array = y_dask_bad_array.rechunk((_rows // 5, 1))
        y_dask_bad_df = ddf.from_dask_array(y_dask_bad_array, columns=['y'])
        y_dask_bad_series = y_dask_bad_df.iloc[:, 0]

        with pytest.raises(ValueError):
            _val_y(y_dask_bad_array)

        with pytest.raises(ValueError):
            _val_y(y_dask_bad_df)

        with pytest.raises(ValueError):
            _val_y(y_dask_bad_series)


    def test_accuracy(self, y_np, y_pd, y_da, y_ddf):

        assert _val_y(list(y_np)) is None

        assert _val_y(tuple(y_np)) is None

        assert _val_y(set(list(y_np))) is None

        assert _val_y(y_np) is None

        assert _val_y(y_pd) is None

        assert _val_y(y_pd.iloc[:, 0]) is None

        assert _val_y(y_da) is None

        assert _val_y(y_ddf) is None

        assert _val_y(y_ddf.iloc[:, 0]) is None




