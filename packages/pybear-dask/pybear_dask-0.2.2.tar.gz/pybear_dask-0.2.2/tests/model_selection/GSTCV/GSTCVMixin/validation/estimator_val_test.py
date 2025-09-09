# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCVMixin._validation._estimator import \
    _val_estimator

from dask_ml.linear_model import (
    LinearRegression as dask_LinearRegression,
    LogisticRegression as dask_LogisticRegression
)
from dask_ml.feature_extraction.text import CountVectorizer as dask_CountVectorizer
from dask_ml.preprocessing import OneHotEncoder as dask_OneHotEncoder

# must be an instance not the class! & be an estimator!



class TestValEstimator:


    @pytest.mark.parametrize('not_instantiated',
        (dask_OneHotEncoder, dask_LinearRegression, dask_LogisticRegression)
    )
    def test_rejects_not_instantiated(self, not_instantiated):

        with pytest.raises(
            TypeError,
            match=f"estimator must be an instance, not the class"
        ):
            _val_estimator(not_instantiated)


    @pytest.mark.parametrize('non_estimator',
        (dask_OneHotEncoder, dask_CountVectorizer)
    )
    def test_rejects_non_estimator(self, non_estimator):

        with pytest.raises(AttributeError):
            _val_estimator(non_estimator())


    @pytest.mark.parametrize('dask_non_classifiers',
        (dask_LinearRegression, )
    )
    def test_rejects_dask_non_classifiers(self, dask_non_classifiers):

        with pytest.raises(AttributeError):
            _val_estimator(dask_non_classifiers())


    @pytest.mark.parametrize('dask_non_classifiers', (dask_LogisticRegression, ))
    def test_accepts_dask_classifiers(self, dask_non_classifiers):

        assert _val_estimator(dask_non_classifiers()) is None





