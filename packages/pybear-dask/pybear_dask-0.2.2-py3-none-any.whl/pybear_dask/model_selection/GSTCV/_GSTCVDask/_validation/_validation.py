# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.GSTCV._type_aliases import ClassifierProtocol

from ....GSTCV._GSTCVDask._validation._dask_estimator import _val_dask_estimator
from ....GSTCV._GSTCVDask._validation._cache_cv import _val_cache_cv
from ....GSTCV._GSTCVDask._validation._iid import _val_iid



def _validation(
    _estimator: ClassifierProtocol,
    _iid: bool,
    _cache_cv: bool
) -> None:
    """Centralized hub for `GSTCVDask` parameter validation.

    See the submodules for more information.

    Parameters
    ----------
    _estimator : ClassifierProtocol
        The estimator passed to `GSTCVDask`.
    _iid : bool
        Whether the data is randomly distributed along the example axis
        or is organized in some non-random way.
    _cache_cv : bool
        Indicates if the train/test folds of the data are to be stored
        when first generated, or if the folds are generated from X, y
        and the KFold indices at each point of need. Caching all the
        folds for each split of the data is memory-intensive.

    Returns
    -------
    None

    """


    _val_dask_estimator(_estimator)

    _val_iid(_iid)

    _val_cache_cv(_cache_cv)




