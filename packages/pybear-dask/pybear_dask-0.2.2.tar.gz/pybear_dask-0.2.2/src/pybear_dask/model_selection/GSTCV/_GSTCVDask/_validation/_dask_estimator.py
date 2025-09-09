# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.GSTCV._type_aliases import ClassifierProtocol

import sys
import warnings

from sklearn.pipeline import Pipeline



def _val_dask_estimator(
    _estimator: ClassifierProtocol
) -> None:
    """Warn if the estimator is not a dask classifier, either from dask
    itself, or from XGBoost or LightGBM.

    The `GSTCVDask` module is expected to most likely encounter dask_ml,
    xgboost, and lightgbm dask estimators. The estimator must be passed
    as an instance, not the class itself.

    Parameters
    ----------
    _estimator : ClassifierProtocol
        the estimator to be validated

    Returns
    -------
    None

    """


    # validate estimator ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    def get_inner_most_estimator(__estimator):

        try:
            if isinstance(__estimator, Pipeline):
                return get_inner_most_estimator(__estimator.steps[-1][-1])
            else:
                return get_inner_most_estimator(__estimator.estimator)
        except:
            return __estimator


    __estimator = get_inner_most_estimator(_estimator)

    try:
        _module = sys.modules[__estimator.__class__.__module__].__file__
    except:
        raise AttributeError(f"'{__estimator.__class__.__name__}' is not "
            f"a valid classifier")

    # 24_08_04 change raise to warn
    # to allow XGBClassifier, reference errors associated with
    # DaskXGBClassifier and dask GridSearch CV
    # 25_06_28 no longer checking for non-dask estimator
    # __ = str(_module).lower()
    # if 'dask_ml' not in __:
    #     warnings.warn(f"'{__estimator.__class__.__name__}' does not "
    #         f"appear to be a dask classifier.")
    # if 'dask' not in __ and 'conftest' not in __:  # allow pytest with
    # mock clf
        # raise TypeError(f"'{__estimator.__class__.__name__}' is not a
        #     f"dask classifier. GSTCVDask can only accept dask classifiers. "
        #     f"\nTo use non-dask classifiers, use the GSTCV package.")

    del get_inner_most_estimator, __estimator, _module

    # END validate estimator ** * ** * ** * ** * ** * ** * ** * ** * **







