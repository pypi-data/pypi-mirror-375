# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear_dask.model_selection.GSTCV._GSTCVDask._validation._dask_estimator \
    import _val_dask_estimator

from sklearn.linear_model import LogisticRegression as sk_LogisticRegression

from dask_ml.linear_model import LogisticRegression as dask_LogisticRegression

# must be an instance not the class! & be an estimator!


class TestValDaskEstimator:

    # 25_06_28 no longer checking for non-dask estimator
    # @pytest.mark.parametrize('non_dask_classifier', (sk_LogisticRegression, ))
    # def test_warns_on_non_dask_classifiers(self, non_dask_classifier):
    #
    #     exp_warn = (f"'{non_dask_classifier().__class__.__name__}' does not "
    #         f"appear to be a dask classifier.")
    #     with pytest.warns(match=exp_warn):
    #         _val_dask_estimator(non_dask_classifier())

        # the old way pre-warn
        # with pytest.raises(TypeError):
        #     _val_dask_estimator(non_dask_classifier())


    @pytest.mark.parametrize('dask_classifiers', (dask_LogisticRegression, ))
    def test_accepts_all_dask_classifiers(self, dask_classifiers):
        # must be an instance not the class! & be a classifier!
        assert _val_dask_estimator(dask_classifiers()) is None








