# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._validation import \
    _validation

import pytest

from dask_ml.linear_model import LogisticRegression as dask_logistic



class TestValidation:

    # def _validation(
    #     _estimator: ClassifierProtocol,
    #     _iid: bool,
    #     _cache_cv: bool
    # ) -> None:


    @pytest.mark.parametrize('_estimator', (dask_logistic(), ))
    @pytest.mark.parametrize('_iid', (True, False))
    @pytest.mark.parametrize('_cache_cv', (True, False))
    def test_accuracy(self, _estimator, _iid, _cache_cv):

        # each of the submodules has their own test. just verify this
        # works and passes good.

        assert _validation(_estimator, _iid, _cache_cv) is None





