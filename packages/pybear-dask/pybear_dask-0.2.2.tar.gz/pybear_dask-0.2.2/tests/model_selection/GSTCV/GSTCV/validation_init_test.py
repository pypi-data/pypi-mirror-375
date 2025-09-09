# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from dask_ml.linear_model import (
    LinearRegression as dask_LinearRegression,
    LogisticRegression as dask_LogisticRegression
)

from pybear.model_selection.GSTCV._GSTCV.GSTCV import GSTCV



class TestInitValidation:


    # fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    @staticmethod
    @pytest.fixture(scope='function')
    def special_gstcv(
        sk_est_log, param_grid_sk_log, standard_cv_int,
        standard_error_score, standard_WIP_scorer
    ):
        # dont overwrite a session fixture with new params! create a new one.

        return GSTCV(
            estimator=sk_est_log,
            param_grid=param_grid_sk_log,
            thresholds=np.linspace(0,1,11),
            cv=standard_cv_int,
            error_score=standard_error_score,
            verbose=10,
            scoring=standard_WIP_scorer,
            refit=False,
            n_jobs=-1,
            pre_dispatch='2*n_jobs',
            return_train_score=True
        )

    # END fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    # estimator v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    # must be an instance not the class! & be a classifier!

    def test_estimator_rejects_dask_non_classifier(self, special_gstcv, X_np, y_np):

        special_gstcv.set_params(estimator=dask_LinearRegression())

        with pytest.raises(AttributeError):
            special_gstcv.fit(X_np, y_np)


    def test_estimator_rejects_dask_classifier(self, special_gstcv, X_np, y_np):

        special_gstcv.set_params(estimator=dask_LogisticRegression())

        with pytest.raises(TypeError):
            special_gstcv.fit(X_np, y_np)

    # END estimator v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^




