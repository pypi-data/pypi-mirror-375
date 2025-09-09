# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import Iterable

import numbers

import numpy as np
from dask import compute
import dask.array as da
import dask.dataframe as ddf



def _val_y(
    _y: Iterable[int]  # not DaskYType... see the notes.
) -> None:
    """Validate `_y`.

    `_y` must be single label and binary in [0, 1].

    The validation is considerably looser than what would be for
    DaskYType. This allows *any* 1D container holding 0's and 1's.
    Let the estimator raise an error if there is a problem with the
    container.

    Parameters
    ----------
    _y : vector-like of shape (n_samples,) or (n_samples, 1)
        The target for the data.

    Returns
    -------
    None

    """


    # y ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    if hasattr(_y, 'shape'):
        if hasattr(_y, 'compute'):
            y_shape = compute(*_y.shape)
        else:
            y_shape = _y.shape
    else:
        try:
            y_shape = np.array(_y).shape
            if isinstance(_y, set):
                y_shape = np.array(list(_y)).shape
        except:
            raise TypeError(f"'y' must have a 'shape' attribute.")


    _err_msg = (
        f"GSTCVDask can only perform thresholding on vector-like binary "
        f"targets with values in [0,1]. \nPass 'y' as a vector of 0's and 1's."
    )

    if len(y_shape) == 1:
        pass
    elif len(y_shape) == 2:
        if y_shape[1] != 1:
            raise ValueError(_err_msg)
    else:
        raise ValueError(_err_msg)


    if isinstance(_y, da.core.Array):
        _unique = set(da.unique(_y).compute())
    elif isinstance(_y, (ddf.DataFrame, ddf.Series)):
        _unique = set(da.unique(_y.to_dask_array(lengths=True)).compute())
    elif hasattr(_y, 'shape'):
        _unique = set(np.unique(_y))
    else:
        _unique = set(np.unique(list(_y)))


    if not _unique.issubset({0, 1}):
        raise ValueError(_err_msg)

    del _unique




