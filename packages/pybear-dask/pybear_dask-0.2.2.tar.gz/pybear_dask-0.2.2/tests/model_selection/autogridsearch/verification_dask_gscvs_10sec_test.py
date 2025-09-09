# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# This test module verifies that agscv works for all dask GSCV modules.



import pytest

from pybear.model_selection.autogridsearch.autogridsearch_wrapper import \
    autogridsearch_wrapper

from dask_ml.model_selection import (
    GridSearchCV as DaskGridSearchCV,
    RandomizedSearchCV as DaskRandomizedSearchCV,
    IncrementalSearchCV,
    HyperbandSearchCV,
    SuccessiveHalvingSearchCV,
    InverseDecaySearchCV
)



# ** * ** * ** * ** * ** ** * ** * ** * ** * ** ** * ** * ** * ** * **
# dask gscvs that dont need a partial_fit exposed ** * ** * ** * ** * **

class TestDaskGSCVSThatDontNeedPartialFit:

    #         estimator,
    #         params: ParamsType,
    #         total_passes: int = 5,
    #         total_passes_is_hard: bool = False,
    #         max_shifts: None | int = None,
    #         agscv_verbose: bool = False,
    #         **parent_gscv_kwargs


    @pytest.mark.parametrize('DASK_GSCV',
        (DaskGridSearchCV, DaskRandomizedSearchCV)
    )
    @pytest.mark.parametrize('_total_passes', (2, ))
    @pytest.mark.parametrize('_scorer',
        ('accuracy', ['accuracy', 'balanced_accuracy'])
    )
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (1, ))
    @pytest.mark.parametrize('_refit', ('accuracy', False, lambda x: 0))
    def test_dask_gscvs(self, dask_estimator_1, dask_params_1, DASK_GSCV,
        _total_passes, _scorer, _tpih, _max_shifts, _refit, X_da, y_da # _client
    ):

        # faster without client


        AGSCV_params = {
            'estimator': dask_estimator_1,
            'params': dask_params_1,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'scoring': _scorer,
            'n_jobs': -1,
            'cv': 4,
            'error_score': 'raise',
            'return_train_score': False,
            'refit': _refit,
            'iid': True,
            'cache_cv': True,
            'scheduler': None
        }

        AutoGridSearch = autogridsearch_wrapper(DASK_GSCV)(**AGSCV_params)

        # 25_04_19 changed fit() to raise ValueError when best_params_
        # is not exposed. it used to be that agscv code was shrink-wrapped
        # around dask gscv quirks as to when it does/doesnt expose
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
        except Exception as hell:
            raise hell

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert AutoGridSearch.total_passes >= _total_passes
        assert AutoGridSearch.total_passes_is_hard is _tpih
        assert AutoGridSearch.max_shifts == _max_shifts
        assert AutoGridSearch.agscv_verbose is False
        assert AutoGridSearch.scoring == _scorer
        assert AutoGridSearch.refit == _refit

        if _refit:
            assert isinstance(
                AutoGridSearch.best_estimator_, type(dask_estimator_1)
            )
        elif not _refit:
            with pytest.raises(AttributeError):
                AutoGridSearch.best_estimator_


        best_params_ = AutoGridSearch.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(dask_params_1))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str) for _ in dask_params_1)
        ))

        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# END dask gscvs that dont need a partial_fit exposed ** * ** * ** * ** *
# ** * ** * ** * ** * ** ** * ** * ** * ** * ** ** * ** * ** * ** * **



# ** * ** * ** * ** * ** ** * ** * ** * ** * ** ** * ** * ** * ** * **
# dask gscvs that need a partial_fit exposed ** * ** * ** * ** * ** * ** *

# RuntimeError: Attempting to use an asynchronous Client in a synchronous context of `dask.compute`
@pytest.mark.skip(reason=f"as of 25_04_18 fails for async client. does anybody care.")
class TestDaskGSCVSThatNeedPartialFitButNotSuccessiveHalving:

    #         estimator,
    #         params: ParamsType,
    #         total_passes: int = 5,
    #         total_passes_is_hard: bool = False,
    #         max_shifts: None | int = None,
    #         agscv_verbose: bool = False,
    #         **parent_gscv_kwargs


    # dask_estimator_2 needs to have partial_fit() for Incremental
    @pytest.mark.parametrize('DASK_GSCV',
         (IncrementalSearchCV, HyperbandSearchCV, InverseDecaySearchCV)
    )
    @pytest.mark.parametrize('_total_passes', (2, ))
    @pytest.mark.parametrize('_scorer', (['accuracy'], ))
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (1, ))
    def test_dask_gscvs(self, DASK_GSCV, dask_estimator_2, dask_params_2,
        _total_passes, _scorer, _tpih, _max_shifts, X_da, y_da, _client
    ):

        # cannot accept multiple scorers
        # THIS ONE NEEDS A CLIENT

        AGSCV_params = {
            'estimator': dask_estimator_2,
            'params': dask_params_2,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'scoring': _scorer,
            'verbose': False,
            'random_state': None,
            'tol': 0.0001,
            'prefix': '',
            'test_size': None,
            'patience': False,
            'max_iter': 100,
            # 'n_initial_parameters': 10,
            # 'decay_rate': 10,
            # 'n_initial_iter': None,
            # 'fits_per_score': 1,
            # 'aggressiveness': 3,
            # 'predict_meta': None,
            # 'predict_proba_meta': None,
            # 'transform_meta': None,
            # 'scores_per_fit': None
        }

        AutoGridSearch = autogridsearch_wrapper(DASK_GSCV)(**AGSCV_params)

        AutoGridSearch.fit(X_da, y_da, classes=(0, 1))

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **
        assert AutoGridSearch.total_passes >= _total_passes
        assert AutoGridSearch.total_passes_is_hard is _tpih
        assert AutoGridSearch.max_shifts == _max_shifts
        assert AutoGridSearch.agscv_verbose is False
        if isinstance(_scorer, list) and len(_scorer) == 1:
            assert AutoGridSearch.scoring == _scorer[0]
        else:
            assert AutoGridSearch.scoring == _scorer


        assert isinstance(AutoGridSearch.best_estimator_, type(dask_estimator_2))

        best_params_ = AutoGridSearch.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(dask_params_2))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str) for _ in dask_params_2)
        ))


        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **


# RuntimeError: Attempting to use an asynchronous Client in a synchronous context of `dask.compute`
@pytest.mark.skip(reason=f"as of 25_04_18 fails for async client. does anybody care.")
class TestDaskSuccessiveHalving:

    #         estimator,
    #         params: ParamsType,
    #         total_passes: int = 5,
    #         total_passes_is_hard: bool = False,
    #         max_shifts: None | int = None,
    #         agscv_verbose: bool = False,
    #         **parent_gscv_kwargs


    @pytest.mark.parametrize('DASK_GSCV', (SuccessiveHalvingSearchCV, ))
    @pytest.mark.parametrize('_total_passes', (2, ))
    @pytest.mark.parametrize('_scorer', (['accuracy'], ))
    @pytest.mark.parametrize('_tpih', (True, ))
    @pytest.mark.parametrize('_max_shifts', (1, ))
    def test_dask_gscvs(self, DASK_GSCV, dask_estimator_2, dask_params_2,
        _total_passes, _scorer, _tpih, _max_shifts, X_da, y_da, _client
    ):

        # cannot accept multiple scorers
        # THIS ONE NEEDS A CLIENT

        AGSCV_params = {
            'estimator': dask_estimator_2,
            'params': dask_params_2,
            'total_passes': _total_passes,
            'total_passes_is_hard': _tpih,
            'max_shifts': _max_shifts,
            'agscv_verbose': False,
            'scoring': _scorer,
            'verbose': False,
            'random_state': None,
            'tol': 1e-3,
            'prefix': '',
            'test_size': None,
            'patience': False,
            'max_iter': None,
            'n_initial_parameters': 10,
            'n_initial_iter': 3,
            'aggressiveness': 3
        }

        AutoGridSearch = autogridsearch_wrapper(DASK_GSCV)(**AGSCV_params)

        AutoGridSearch.fit(X_da, y_da, classes=(0, 1))

        # assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
        assert AutoGridSearch.total_passes >= _total_passes
        assert AutoGridSearch.total_passes_is_hard is _tpih
        assert AutoGridSearch.max_shifts == _max_shifts
        assert AutoGridSearch.agscv_verbose is False
        if isinstance(_scorer, list) and len(_scorer) == 1:
            assert AutoGridSearch.scoring == _scorer[0]
        else:
            assert AutoGridSearch.scoring == _scorer

        assert isinstance(AutoGridSearch.best_estimator_, type(dask_estimator_2))

        best_params_ = AutoGridSearch.best_params_
        assert isinstance(best_params_, dict)
        assert sorted(list(best_params_)) == sorted(list(dask_params_2))
        assert all(map(
            isinstance,
            best_params_.values(),
            ((int, float, bool, str) for _ in dask_params_2)
        ))


        # END assertions ** * ** * ** * ** * ** * ** * ** * ** * ** * **

# END dask gscvs that need a partial_fit exposed ** * ** * ** * ** * **
# ** * ** * ** * ** * ** ** * ** * ** * ** * ** ** * ** * ** * ** * **





