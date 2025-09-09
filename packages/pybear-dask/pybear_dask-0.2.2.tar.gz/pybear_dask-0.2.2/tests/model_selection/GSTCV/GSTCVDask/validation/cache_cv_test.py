# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._cache_cv import \
    _val_cache_cv



class TestValCacheCV:


    @pytest.mark.parametrize('junk_cache_cv',
        (0, 1, 3.14, None, min, 'junk', [0,1], (0,1), {0,1}, {'a':1}, lambda x: x)
    )
    def test_rejects_all_non_bool(self, junk_cache_cv):
        with pytest.raises(TypeError):
            _val_cache_cv(junk_cache_cv)


    @pytest.mark.parametrize('good_cache_cv', (True, False))
    def test_accepts_bool(self, good_cache_cv):
        assert _val_cache_cv(good_cache_cv) is None




