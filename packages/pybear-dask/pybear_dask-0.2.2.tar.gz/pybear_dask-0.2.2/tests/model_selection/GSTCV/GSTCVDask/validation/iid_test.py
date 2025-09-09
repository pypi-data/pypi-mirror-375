# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._iid import _val_iid



class TestValIID:


    @pytest.mark.parametrize('junk_iid',
        (0, 1, 3.14, None, min, 'junk', [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rejects_all_non_bool(self, junk_iid):
        with pytest.raises(TypeError):
            _val_iid(junk_iid)


    @pytest.mark.parametrize('good_iid', (True, False))
    def test_accepts_bool(self, good_iid):
        assert _val_iid(good_iid) is None






