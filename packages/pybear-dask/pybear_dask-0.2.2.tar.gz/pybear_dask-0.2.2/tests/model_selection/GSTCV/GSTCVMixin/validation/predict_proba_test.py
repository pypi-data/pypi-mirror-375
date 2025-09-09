# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import dask.array as da

from pybear.model_selection.GSTCV._GSTCVMixin._validation._predict_proba \
    import _val_predict_proba



class TestValPredictProba:


    @pytest.mark.parametrize('_format',
        ('da', 'ddf')
    )
    @pytest.mark.parametrize('_dim', (1, 2))
    @pytest.mark.parametrize('_len', (2, 5, 10, 100))
    def test_accepts_good_pp(self, _format_helper, _format, _dim, _len):

        if _format == 'py_set' and _dim == 2:
            pytest.skip(reason=f'cant have 2D set')
        # END skip impossible ** * ** * ** * ** * ** * ** * ** * ** * **

        good_pp = _format_helper(
            da.random.uniform(0, 1, (_len,)), _format, _dim
        )


        assert _val_predict_proba(good_pp, _len) is None






