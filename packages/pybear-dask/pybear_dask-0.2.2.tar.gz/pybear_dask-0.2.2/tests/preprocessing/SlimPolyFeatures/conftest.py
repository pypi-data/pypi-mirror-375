# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np



@pytest.fixture(scope='module')
def _shape():
    return (20, 4)


@pytest.fixture(scope='module')
def X_np(_X_factory, _shape):
    # make be float64 so scipy sparse can take it
    return _X_factory(
        _dupl=None,
        _has_nan=False,
        _dtype='int',
        _shape=_shape
    ).astype(np.float64)



@pytest.fixture(scope='module')
def y_np(_shape):
    return np.random.randint(0, 2, (_shape[0],))


@pytest.fixture(scope='function')
def _kwargs():

    return {
        'degree': 2,
        'min_degree': 1,
        'interaction_only': True,
        'scan_X': False,
        'keep': 'first',
        'sparse_output': False,
        'feature_name_combiner': "as_indices",
        'equal_nan': True,
        'rtol': 1e-5,
        'atol': 1e-8,
        'n_jobs': 1,  # leave set at 1 because of confliction
        'job_size': 20
    }




