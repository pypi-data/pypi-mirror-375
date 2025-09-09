# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


import pytest

import pybear_dask


class TestVersion:

    def test_version(self):

        version_str = pybear_dask.__version__
        version_tuple = pybear_dask.__version_tuple__

        # __version__ is string, is decimal
        assert isinstance(version_str, str)
        assert sum(map(lambda x: x == '.', version_str)) == 2

        # __version__ is made of integers
        _fst_dot = version_str.find('.', 1)
        _scnd_dot = version_str.find('.', 2)
        int(version_str[:_fst_dot])
        int(version_str[_fst_dot + 1:_scnd_dot])
        int(version_str[_scnd_dot + 1:])

        # __version_tuple__ is tuple of integers
        assert isinstance(version_tuple, tuple)
        assert int(version_tuple[0]) == version_tuple[0]
        assert int(version_tuple[1]) == version_tuple[1]
        assert int(version_tuple[2]) == version_tuple[2]





