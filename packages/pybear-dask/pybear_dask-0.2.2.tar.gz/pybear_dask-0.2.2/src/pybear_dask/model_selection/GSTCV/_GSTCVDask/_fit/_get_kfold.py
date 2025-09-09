# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Iterator,
)
from .._type_aliases import (
    DaskXType,
    DaskYType,
    DaskKFoldType
)

import time

from dask_ml.model_selection import KFold as dask_KFold



def _get_kfold(
    _X: DaskXType,
    _n_splits: int,
    _iid: bool,
    _verbose: int,
    _y: DaskYType | None = None
) -> Iterator[DaskKFoldType]:
    """Use dask_ml KFold to get train / test splits when cv is passed as
    an integer.

    KFold uses the number of rows in `_X` and `_n_splits` to determine
    the indices in each train / test split. 'y' is optional in dask_ml
    KFold. If passed, the number of rows in `_X` and `_y` must be equal.

    *** IMPORTANT!!!
    This function can be called multiple times within a single param grid
    permutation, first to fit, again to get test score, then again if
    `return_train_score`. Therefore, it must return the same indices for
    each call. The only things that should cause indices to be different
    are `_n_splits` and the number of rows in `_X`. Since this is dask
    KFold, there is the wildcard of the `_iid` setting. If `_iid` is
    False -- meaning the data is known to have some non-random grouping
    along axis 0 -- via the 'shuffle' argument KFold will generate
    indices that sample across chunks to randomize the data in the
    splits. In that case, fix the 'random_state' parameter to make
    selection repeatable. If `_iid` is True, 'shuffle' is False,
    'random_state' can be None, and the splits should be repeatable.

    Parameters
    ----------
    _X : DaskXType
        The data to be split.
    _n_splits : int
        The number of splits to produce; the number of split pairs
        yielded by the returned generator object.
    _iid : bool
        True, the examples in X are distributed randomly; False,
        there is some kind of non-random ordering of the examples in X.
    _verbose : int
        A number from 0 to 10 indicating the amount of information to
        display to screen during the grid search trials. 0 means no
        output, 10 means full output.
    _y : DaskYType | None, default = None
        The target the data is being fit against, to be split in the
        same way as the data.

    Returns
    -------
    KFOLD : Iterator[DaskKFoldType]
        A generator object yielding pairs of train test indices as
        da.core.Array[int].

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    # 25_04_29 NOT VALIDATING X & y HERE ANYMORE. LET KFold RAISE.
    assert isinstance(_n_splits, int)
    assert _n_splits > 1
    assert isinstance(_iid, bool)
    try:
        float(_verbose)
    except:
        raise AssertionError(f"'_verbose' must be numeric")
    assert _verbose >= 0
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    split_t0 = time.perf_counter()
    # KFold keeps the same chunks ax X
    # as of 25_04_29 dask_KFold only accepts da array for X
    KFOLD = dask_KFold(
        n_splits=_n_splits,
        shuffle=not _iid,
        random_state=7 if not _iid else None,
        # shuffle is on if not iid. must use random_state so that later
        # calls for train score get same splits.
    ).split(_X, _y)


    if _verbose >= 5:
        print(f'split time = {time.perf_counter() - split_t0: ,.3g} s')

    del split_t0

    return KFOLD








