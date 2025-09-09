# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from typing import (
    ContextManager,
    Iterable,
    Sequence,
    TypeAlias
)

import dask
import distributed



DaskXType: TypeAlias = Iterable
DaskYType: TypeAlias = Sequence[int] | None

DaskSlicerType: TypeAlias = dask.array.core.Array

DaskKFoldType: TypeAlias = tuple[DaskSlicerType, DaskSlicerType]

DaskSplitType: TypeAlias = tuple[DaskXType, DaskYType]

DaskSchedulerType: TypeAlias = (
    distributed.scheduler.Scheduler
    | distributed.client.Client
    | ContextManager
 )  # nullcontext





