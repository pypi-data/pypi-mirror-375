# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCV._validation._sk_estimator import \
    _val_sk_estimator

from dask_ml.linear_model import LogisticRegression as dask_LogisticRegression


# must be an instance not the class! & be an estimator!


class TestValSkEstimator:


    @pytest.mark.parametrize('dask_classifiers', (dask_LogisticRegression, ))
    def test_rejects_all_dask_classifiers(self, dask_classifiers):
        # must be an instance not the class! & be a classifier!
        with pytest.raises(TypeError):
            _val_sk_estimator(dask_classifiers())



