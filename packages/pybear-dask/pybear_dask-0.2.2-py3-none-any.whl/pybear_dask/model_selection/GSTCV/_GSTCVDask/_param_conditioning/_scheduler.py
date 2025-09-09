# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from .._type_aliases import DaskSchedulerType

import contextlib

from distributed import (
    Client,
    get_client
)



def _cond_scheduler(
    _scheduler: DaskSchedulerType | None,
    _n_jobs: int | None
) -> DaskSchedulerType:
    """Set the dask scheduler.

    The passed scheduler supersedes all other external schedulers. If
    "None" was passed to the scheduler kwarg of GSTCVDask (the default),
    look for an external context manager or global scheduler using
    `get_client`. If one exists, use nullcontext as an internal context
    manager to not interfere with the external scheduler. If "None" was
    passed to the scheduler kwarg of `GSTCVDask` and there is no external
    scheduler, instantiate `distributed.Client`, which defaults to
    `LocalCluster`, with `n_workers`=`n_jobs` and 1 thread per worker.
    If `n_jobs` is None, uses the default `distributed.Client` behavior
    when `n_workers` is set to None.

    If a scheduler is passed, this module does not perform any validation
    but allows that to be handled by dask at compute time.

    This module intentionally deviates from the dask_ml API, and
    disallows any shorthand methods for setting up a scheduler (such
    as strings like 'threading' and 'multiprocessing', which are
    ultimately passed to dask.base.get_scheduler.) All of these types
    of configurations should be handled by the user external to the
    `GSTCVDask` module. As much as possible, dask and distributed
    objects are allowed to flow through without any hard-coded input.

    Parameters
    ----------
    _scheduler : SchedulerType | None
        _scheduler to be validated and used for compute

    Returns
    -------
    _scheduler : DaskSchedulerType
        Validated, instantiated scheduler

    """


    if _scheduler is None:
    # if there is no hard scheduler...
        try:
            # ...try to get an existing client...
            get_client()
            # if a client is available (either an external context manager
            # or a default scheduler in an outer scope) let that scheduler
            # take precedence. set _scheduler to nullcontext for empty
            # internal context managers.
            _scheduler = contextlib.nullcontext()
        except ValueError:
            # ...if no external client and no hard scheduler (client),
            # create a new one
            _scheduler = Client(n_workers=_n_jobs, threads_per_worker=1)

    else:
    # if there is a hard scheduler, that supersedes all.
        pass


    return _scheduler





