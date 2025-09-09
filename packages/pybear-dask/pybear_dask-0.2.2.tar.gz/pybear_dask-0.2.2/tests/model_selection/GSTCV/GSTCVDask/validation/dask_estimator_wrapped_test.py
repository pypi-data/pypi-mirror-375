# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._dask_estimator \
    import _val_dask_estimator

from sklearn.preprocessing import OneHotEncoder as sk_OneHotEncoder

from sklearn.linear_model import (
    RidgeClassifier as sk_RidgeClassifier, # wrap with CCCV
    LogisticRegression as sk_LogisticRegression,
    SGDClassifier as sk_SGDClassifier
)

from sklearn.calibration import CalibratedClassifierCV # wrap around RidgeClassifier

from sklearn.feature_extraction.text import CountVectorizer as sk_CountVectorizer
from sklearn.pipeline import Pipeline

# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

from dask_ml.linear_model import LogisticRegression as dask_LogisticRegression

from dask_ml.feature_extraction.text import CountVectorizer as dask_CountVectorizer
from dask_ml.preprocessing import OneHotEncoder as dask_OneHotEncoder



# must be an instance not the class! & be an estimator!

class TestValWrappedDaskEstimator:

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    @pytest.mark.parametrize('non_dask_est',
        (sk_RidgeClassifier, sk_SGDClassifier)
    )
    def test_warns_on_non_dask_CCCV(self, non_dask_est):

        # 25_06_28 no longer checking for non-dask estimator
        # exp_warn = (f"'{non_dask_est().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):

        assert _val_dask_estimator(
            CalibratedClassifierCV(self._pipeline(non_dask_est()))
        ) is None


    def test_accepts_dask_CCCV(self):

        assert _val_dask_estimator(
            CalibratedClassifierCV(self._pipeline(dask_LogisticRegression()))
        ) is None

    # END CCCV ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # pipeline - 2 inner objects ** * ** * ** * ** * ** * ** * ** * ** *

    def _pipeline(self, _estimator_instance):
        return Pipeline(
            steps=[
                ('ct_vect', sk_CountVectorizer()),
                ('clf', _estimator_instance)
            ]
        )


    @pytest.mark.parametrize('non_dask_classifier', (sk_LogisticRegression, ))
    def test_warns_on_non_dask_classifiers(self, non_dask_classifier):

        # 25_06_28 no longer checking for non-dask estimator
        # exp_warn = (f"'{non_dask_classifier().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):

        assert _val_dask_estimator(self._pipeline(non_dask_classifier())) is None

        # the old way pre-warn
        # with pytest.raises(TypeError):
        #     _val_dask_estimator(self._pipeline(non_dask_classifier()))


    @pytest.mark.parametrize('dask_classifiers', (dask_LogisticRegression, ))
    def test_accepts_good_pipeline_1(self, dask_classifiers):
        # must be an instance not the class! & be a classifier!
        assert _val_dask_estimator(self._pipeline(dask_classifiers())) is None


    @pytest.mark.parametrize('good_pipeline_steps',
        ([('onehot', dask_OneHotEncoder()), ('logistic', dask_LogisticRegression())],)
    )
    def test_accepts_good_pipeline_2(self, good_pipeline_steps):

        assert _val_dask_estimator(Pipeline(steps=good_pipeline_steps)) is None


    def test_warns_on_wrapped_non_dask_CCCV(self):

        # 25_06_28 no longer checking for non-dask estimator
        # exp_warn = (f"'{sk_RidgeClassifier().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):
        assert _val_dask_estimator(
            self._pipeline(CalibratedClassifierCV(sk_RidgeClassifier()))
        ) is None

        # exp_warn = (f"'{sk_SGDClassifier().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):
        assert _val_dask_estimator(
            self._pipeline(CalibratedClassifierCV(sk_SGDClassifier()))
        ) is None


    def test_accepts_wrapped_dask_CCCV(self):
        assert _val_dask_estimator(
            self._pipeline(CalibratedClassifierCV(dask_LogisticRegression()))
        ) is None

    # END pipeline - 2 inner objects ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
    # pipeline - 3 inner objects ** * ** * ** * ** * ** * ** * ** * ** *

    @staticmethod
    @pytest.fixture
    def sk_pipeline():
        # must be an instance not the class!
        return Pipeline(
            steps=[
                ('sk_CountVectorizer', sk_CountVectorizer()),
                ('sk_OneHotEncoder', sk_OneHotEncoder()),
                ('sk_Logistic', sk_LogisticRegression())
            ],
            verbose=0
        )


    @staticmethod
    @pytest.fixture
    def dask_pipeline_1():
        # must be an instance not the class!
        return Pipeline(
            steps=[
                ('dask_CountVectorizer', dask_CountVectorizer()),
                ('dask_OneHotEncoder', dask_OneHotEncoder()),
                ('dask_Logistic', dask_LogisticRegression())
            ],
            verbose=0
        )


    @staticmethod
    @pytest.fixture
    def dask_pipeline_2():
        # must be an instance not the class!
        return Pipeline(
            steps=[
                ('sk_CountVectorizer', sk_CountVectorizer()),
                ('sk_OneHotEncoder', sk_OneHotEncoder()),
                ('dask_Logistic', dask_LogisticRegression())
            ],
            verbose=0
        )


    @staticmethod
    @pytest.fixture
    def dask_pipeline_3():
        # must be an instance not the class!
        return Pipeline(
            steps=[
                ('dask_CountVectorizer', dask_CountVectorizer()),
                ('dask_OneHotEncoder', dask_OneHotEncoder()),
                ('sk_Logistic', sk_LogisticRegression())
            ],
            verbose=0
        )


    def test_accuracy_pipeline(self,
        sk_pipeline, dask_pipeline_1, dask_pipeline_2, dask_pipeline_3
    ):

        # 25_06_28 no longer checking for non-dask estimator
        # exp_warn = (f"'{sk_LogisticRegression().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):
        assert _val_dask_estimator(sk_pipeline) is None

        # the old way pre-warn
        # with pytest.raises(TypeError):
        #     _val_dask_estimator(sk_pipeline)

        assert _val_dask_estimator(dask_pipeline_1) is None
        assert _val_dask_estimator(dask_pipeline_2) is None

        # exp_warn = (f"'{sk_LogisticRegression().__class__.__name__}' does not "
        #     f"appear to be a dask classifier.")
        # with pytest.warns(match=exp_warn):
        assert _val_dask_estimator(dask_pipeline_3) is None

        # the old way pre-warn
        # with pytest.raises(TypeError):
        #     _val_dask_estimator(dask_pipeline_3)


    # END pipeline - 3 inner objects ** * ** * ** * ** * ** * ** * ** *
    # ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **





