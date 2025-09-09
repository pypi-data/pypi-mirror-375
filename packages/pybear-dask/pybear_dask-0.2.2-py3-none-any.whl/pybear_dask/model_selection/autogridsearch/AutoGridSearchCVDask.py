# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Any,
    Sequence
)

from pybear.model_selection import autogridsearch_wrapper
from pybear.model_selection.autogridsearch import autogridsearch_docs

from dask_ml.model_selection import GridSearchCV as dask_GridSearchCV



class AutoGridSearchCVDask(autogridsearch_wrapper(dask_GridSearchCV)):


    __doc__ = autogridsearch_docs.__doc__


    def __init__(
        self,
        estimator,
        params: dict[str, Sequence[tuple[Sequence[Any], int | Sequence[int], str]]],
        *,
        total_passes:int = 5,
        total_passes_is_hard:bool = False,
        max_shifts:int | None = None,
        agscv_verbose:bool = False,
        **parent_gscv_kwargs
    ):

        """Initialize the `AutoGridSearchCVDask` instance."""

        super().__init__(
            estimator,
            params,
            total_passes=total_passes,
            total_passes_is_hard=total_passes_is_hard,
            max_shifts=max_shifts,
            agscv_verbose=agscv_verbose,
            **parent_gscv_kwargs
        )







