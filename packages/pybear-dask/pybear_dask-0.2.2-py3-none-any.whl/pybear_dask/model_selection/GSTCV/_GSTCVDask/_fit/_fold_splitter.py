# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import (
    DaskSlicerType,
    DaskSplitType,
    DaskXType,
    DaskYType
)

import dask.array as da
import dask.dataframe as ddf



def _fold_splitter(
    train_idxs: DaskSlicerType,
    test_idxs: DaskSlicerType,
    *data_objects: DaskXType | DaskYType
) -> tuple[DaskSplitType, ...]:
    """Split given data objects into train / test pairs using the given
    train and test indices.

    The train and test indices independently slice the given data objects;
    the entire data object need not be consumed in a train / test split
    and the splits can also possibly share indices. Standard indexing
    rules apply. Returns a tuple whose length is equal to the number of
    data objects passed, holding tuples of the train / test splits for
    the respective data objects. `train_idxs` and `test_idxs` must be 1D
    vectors of indices, not booleans.

    Parameters
    ----------
    train_idxs : DaskSlicerType
        1D vector of row indices used to slice train sets out of every
        given data object.
    test_idxs : DaskSlicerType
        1D vector of row indices used to slice test sets out of every
        given data object.
    *data_objects : DaskXType | DaskYType
        The data objects to slice. Need not be of equal size, and need
        not be completely consumed in the train / test splits. However,
        standard indexing rules apply when slicing by `train_idxs` and
        `test_idxs`.

    Returns
    -------
    SPLITS : tuple[DaskSplitType, ...]
        Return the train / test splits for the given data objects in the
        order passed in a tuple of tuples, each inner tuple containing a
        train/test pair.

    """


    SPLITS = []
    for _data in data_objects:

        # the compute()s need to be here for ddf slicing to work
        if isinstance(_data, da.core.Array):
            _data_train = _data[train_idxs]
            _data_test = _data[test_idxs]
        elif isinstance(_data, ddf.DataFrame):
            _data_train = _data.loc[train_idxs.compute(), :]
            _data_test = _data.loc[test_idxs.compute(), :]
        elif isinstance(_data, ddf.Series):
            _data_train = _data[train_idxs.compute()]
            _data_test = _data[test_idxs.compute()]
        else:
             raise TypeError(f"disallowed container '{type(_data)}'")

        SPLITS.append(tuple((_data_train, _data_test)))


    return tuple(SPLITS)




