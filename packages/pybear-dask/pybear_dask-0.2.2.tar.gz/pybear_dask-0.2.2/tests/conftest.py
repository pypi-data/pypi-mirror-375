# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from distributed import Client



@pytest.fixture(scope='session')
def _client():
    client = Client(n_workers=1, threads_per_worker=1)
    yield client
    client.close()



