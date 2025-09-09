# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    Callable,
    Literal
)

from ...GSTCV._GSTCVDask import GSTCVDask



def _refit_can_be_skipped(
    _GridSearchParent,
    _scoring: None | str | list | Callable | dict | Literal[False],
    _total_passes: int
) -> bool:
    """Determine if the parent GridSearch, the scoring strategy, and the
    total number of passes allow for refits to be skipped until the
    final pass.

    `best_params_` needs to be exposed on every pass. Some GridSearch
    parents require that `refit` be True to expose `best_params_`. All
    require that `refit` be specified if `scoring` is multiple scorers
    to expose `best_params_`. Refit cannot be skipped if agscv is only
    running one pass.

    This ignores whether `refit` was originally passed as False. If it
    was, then this module will still allow agscv to overwrite pre-final
    pass `refit` with False, which is just overwriting the same value.

    Parameters
    ----------
    _GridSearchParent : GridSearchCV instance
        The parent GridSearchCV class passed to the agscv wrapper.
    _scoring : None | str | list | Callable | dict | Literal[False]]
        The value passed to the `scoring` parameter of the parent
        GridSearchCV. On the off chance that the parent GridSearch does
        not have a `scoring` parameter, Literal[False] is passed to here.
    _total_passes : int
        The number of grid searches to perform. This number is dynamic
        and can be incremented by agscv during a run, based on the need
        to shift grids and the setting of `total_passes_is_hard`.

    Returns
    -------
    _refit_can_be_skipped : bool
        Whether or not to allow refits to be skipped until the last pass
        of agscv.

    """


    # *** ONLY REFIT ON THE LAST PASS TO SAVE TIME WHEN POSSIBLE ***
    # IS POSSIBLE WHEN PARENT:
    # == has refit param, is not False, AND is using only one scorer
    # IS NOT POSSIBLE WHEN:
    # == total_passes = 1
    # == When using multiple scorers, refit must always be left on
    # because multiple scorers dont expose best_params_ when
    # multiscorer and refit=False
    # == using dask GridSearchCV or dask RandomizedSearchCV, they
    # require refit always be True to expose best_params_.
    # == dask IncrementalSearchCV, HyperbandSearchCV,
    # SuccessiveHalvingSearchCV and InverseDecaySearchCV do not take a
    # refit kwarg.
    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    # dask_ml is the fly in the ointment. Always leave refit as the user
    # passed it. So apply the rules for managing refits to GSTCVDask only.


    # all of these have refit
    _is_candidate_gscv = _GridSearchParent in (GSTCVDask, )

    # if 'scoring' is not available from parent (Literal[False] was sent
    # into here), assume the worst case and set _is_multimetric to True
    # so that refit (if available) will always run
    _is_multimetric = 1
    _is_multimetric -= callable(_scoring)
    _is_multimetric -= isinstance(_scoring, (str, type(None)))
    # sklearn anomaly that list scoring is always multimetric,
    # even if len(list)==1.
    _is_not_multimetric = not bool(_is_multimetric)

    _is_multipass = (_total_passes > 1)
    # *** END ONLY REFIT ON THE LAST PASS TO SAVE TIME ************
    # *************************************************************


    return (_is_candidate_gscv and _is_not_multimetric and _is_multipass)




