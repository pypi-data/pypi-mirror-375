# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from contextlib import nullcontext
from copy import deepcopy

import distributed
from dask.distributed import Client

from pybear_dask.model_selection.GSTCV._GSTCVDask._param_conditioning._scheduler \
    import _cond_scheduler



class TestCondScheduler:


    @staticmethod
    @pytest.fixture
    def marked_client_class():
        class PyBearClient(Client):
            pass

        return PyBearClient


    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    def test_none_w_no_global_returns_a_scheduler(self):
        # for some reason, when running the full tests, this sees an
        # external client and creates a nullcontext. but creates a
        # Client when run alone. maybe it is the conftest client,
        # even though it isnt passed to this test? maybe the conftest
        # client isnt spooled up when these tests are run alone?

        has_external = False
        try:
            distributed.get_client()
            has_external = True
        except:
            pass

        _scheduler = None
        _og_scheduler = deepcopy(_scheduler)

        if has_external:
            assert isinstance(_cond_scheduler(_scheduler, _n_jobs=1), nullcontext)
        else:
            assert isinstance(_cond_scheduler(_scheduler, _n_jobs=1), Client)

        # passed None is not mutated
        assert _scheduler is _og_scheduler


    def test_none_w_global_returns_a_nullcontext(self, _client):
        _scheduler = None
        _og_scheduler = deepcopy(_scheduler)
        assert isinstance(_cond_scheduler(_scheduler, _n_jobs=1), nullcontext)
        assert _scheduler is _og_scheduler


    def test_original_scheduler_is_returned(self, marked_client_class):

        # when a scheduler is passed
        _scheduler = marked_client_class()

        # cant do a deepcopy on _scheduler,
        # TypeError: cannot pickle '_asyncio.Task' object
        # so we cant prove out that _cond_scheduler does not mutate
        # passed arg

        assert isinstance(
            _cond_scheduler(_scheduler, _n_jobs=1),
            marked_client_class
        )





