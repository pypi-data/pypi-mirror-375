# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



def _val_iid(
    _iid: bool
) -> None:
    """Validate `iid`.

    `iid` can only be boolean. Indicates whether the data is believed to
    have random distribution of examples (True) or if the data is
    organized non-randomly in some way (False).

    Parameters
    ----------
    _iid : bool
        To be validated.

    Returns
    -------
    None

    """


    if not isinstance(_iid, bool):
        raise TypeError(f"'iid' must be a bool")







