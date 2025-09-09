# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.model_selection.GSTCV._GSTCV._validation._sk_estimator import \
    _val_sk_estimator

from sklearn.calibration import CalibratedClassifierCV

from dask_ml.linear_model import LogisticRegression as dask_LogisticRegression

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline


# must be an instance not the class! & be an estimator!


class TestValWrappedEstimator:

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def test_rejects_dask_CCCV(self):
        with pytest.raises(TypeError):
            _val_sk_estimator(CalibratedClassifierCV(dask_LogisticRegression()))

    # END CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def _pipeline(self, _estimator_instance):
        return Pipeline(
            steps=[
                ('ct_vect', CountVectorizer()),
                ('clf', _estimator_instance)
            ]
        )


    def test_rejects_wrapped_dask_CCCV(self):
        with pytest.raises(TypeError):
            assert _val_sk_estimator(
                self._pipeline(CalibratedClassifierCV(dask_LogisticRegression()))
            ) is None


    @pytest.mark.parametrize('dask_classifiers', (dask_LogisticRegression, ))
    def test_rejects_all_dask_classifiers(self, dask_classifiers):
        # must be an instance not the class! & be a classifier!
        with pytest.raises(TypeError):
            _val_sk_estimator(self._pipeline(dask_classifiers()))





