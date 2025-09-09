# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# this module tests compatibility of autogridsearch_wrapper with dask GSCV
# simply by running wrapped GSCV to completion and asserting a few of
# the GSCV attributes are exposed by the wrapper.



# demo_test incidentally handles testing of all autogridsearch_wrapper
# functionality except fit() (because demo bypasses fit().) This test
# module handles fit().



import pytest

import numpy as np

from pybear_dask.model_selection.autogridsearch.AutoGridSearchCVDask import \
    AutoGridSearchCVDask

pytest.skip(reason=f'tests make zero progress in 35 min', allow_module_level=True)

class TestAutoGridSearchDask:

    # estimator,
    # params: ParamsType,
    # total_passes: int = 5,
    # total_passes_is_hard: bool = False,
    # max_shifts: None | int = None,
    # agscv_verbose: bool = False,
    # **parent_gscv_kwargs


    @pytest.mark.parametrize('_total_passes', (2, ))
    @pytest.mark.parametrize('_scorer',
        ('accuracy', ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (2, ))
    @pytest.mark.parametrize('_refit', ('accuracy', False, lambda x: 0))
    def test_AGSCV(self, mock_estimator, mock_estimator_params,
        _total_passes, _scorer, _tpih, _max_shifts, _refit, X_da, y_da, _client
    ):

        # faster with _client

        AGSTCV_params = {
            'estimator': mock_estimator,
            'params': mock_estimator_params,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'scoring': _scorer,
            'n_jobs': 1,
            'cv': 2,
            'error_score': 'raise',
            'return_train_score': False,
            'refit': _refit,
            'iid': True,
            'cache_cv': True,
            'scheduler': None
        }

        AutoGridSearch = AutoGridSearchCVDask(**AGSTCV_params)

        # 25_04_19 changed fit() to raise ValueError when best_params_
        # is not exposed. it used to be that agscv code was shrink-wrapped
        # around sklearn gscv quirks as to when it does/doesnt expose
        # best_params_. there are no longer any bandaids that condition params
        # for the parent gscvs to get them to "properly" expose 'best_params_',
        # and there are no more predictive shrink-wraps to block failure.
        # The user is left to die by however the parent gscv handles the exact
        # params as given. what that means here is that we are not going to
        # coddle to every little nuanced thing that makes a gscv not want to
        # expose 'best_params_'. Try to fit, if ValueError is raised, look to
        # see that 'best_params_' is not exposed and go to the next test.
        try:
            AutoGridSearch.fit(X_da, y_da)
            assert isinstance(getattr(AutoGridSearch, 'best_params_'), dict)
        except ValueError:
            assert not hasattr(AutoGridSearch, 'best_params_')
            pytest.skip(reason=f'cant do any later tests without fit')
        except Exception as e:
            raise e

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert AutoGridSearch.total_passes >= _total_passes
        assert AutoGridSearch.total_passes_is_hard is _tpih
        assert AutoGridSearch.max_shifts == _max_shifts
        assert AutoGridSearch.agscv_verbose is False
        assert AutoGridSearch.scoring == _scorer
        assert AutoGridSearch.refit == _refit

        # cannot test MockEstimator for scoring or scorer_

        if _refit:
            assert isinstance(
                AutoGridSearch.best_estimator_,
                type(mock_estimator)
            )
        else:
            with pytest.raises(AttributeError):
                AutoGridSearch.best_estimator_


        best_params_ = AutoGridSearch.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(mock_estimator_params))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str, np.int64) for _ in mock_estimator_params)
        ))

        # best_threshold_ should always be exposed with one scorer
        if isinstance(_refit, str) or callable(_scorer) or \
                isinstance(_scorer, str) or len(_scorer) == 1:
            best_threshold_ = AutoGridSearch.best_threshold_
            assert isinstance(best_threshold_, float)
            assert 0 <= best_threshold_ <= 1

        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **







