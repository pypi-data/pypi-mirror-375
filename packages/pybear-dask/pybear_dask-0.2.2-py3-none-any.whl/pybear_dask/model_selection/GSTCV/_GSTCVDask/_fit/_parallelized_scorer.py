# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.GSTCV._type_aliases import (
    ScorerWIPType,
    ClassifierProtocol,
    ThresholdsWIPType,
    MaskedHolderType
)
from .._type_aliases import (
    DaskXType,
    DaskYType
)

import numbers
import time

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._validation._predict_proba \
    import _val_predict_proba



def _parallelized_scorer(
    _X_test: DaskXType,
    _y_test: DaskYType,
    _FIT_OUTPUT_TUPLE: tuple[ClassifierProtocol, float, bool],
    _f_idx: int,
    _SCORER_DICT: ScorerWIPType,
    _THRESHOLDS: ThresholdsWIPType,
    _error_score: numbers.Real | None,
    _verbose: int
) -> tuple[MaskedHolderType, MaskedHolderType]:

    # dont adjust the spacing, is congruent with train scorer

    """Using the estimators fit on each train fold, use `predict_proba`
    and _X_tests to generate _y_preds and score against the corresponding
    _y_tests using all of the scorers and thresholds.

    Builds one fold layer of the TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE
    and TEST_FOLD_x_THRESHOLD_x_SCORER__SCORE_TIME cubes.

    Parameters
    ----------
    _X_test : DaskXType
        A test partition of the data, matched up with the estimator that
        was trained on the complementary train set.
    _y_test : DaskYType
        The corresponding test partition of the target for the `_X_test`
        partition.
    _FIT_OUTPUT_TUPLE : tuple[ClassifierProtocol, float, bool]
        A tuple holding the fitted estimator, the fit time (not needed
        here), and the fit_excepted boolean (needed here.)
    _f_idx : int
        The zero-based split index of the test partition used here;
        parallelism occurs over the different splits.
    _SCORER_DICT : ScorerWIPType
        A dictionary with scorer name as keys and the scorer callables
        as values. The scorer callables are scoring metrics (or similar),
        not make_scorer.
    _THRESHOLDS : ThresholdsWIPType
        For the current search permutation, there was a mother param
        grid that contained a 'thresholds' parameter, that was separated
        from the mother before building cv_results. This is the vector
        of thresholds from the mother that also mothered this search
        permutation.
    _error_score : numbers.Real | Literal['raise']
        If the training fold complementing this test fold excepted during
        fitting and `error_score` was set to the 'raise' literal, this
        module cannot be reached. Otherwise, a number or number-like was
        passed to `error_score`. If 'fit_excepted' is True, this module
        puts the `error_score` value in every position of the
        TEST_THRESHOLD_x_SCORER__SCORE_LAYER array. If `error_score` is
        set to np.nan, that layer is also masked. Every value in
        TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER is set to np.nan and
        masked.
    _verbose : int
        A number from 0 to 10 that indicates the amount of information
        to display to the screen during the grid search process. 0 means
        no output, 10 means maximum output.

    Returns
    -------
    __ : tuple[np.ma.MaskedArray, np.ma.MaskedArray]
        TEST_THRESHOLD_x_SCORER__SCORE_LAYER : MaskedHolderType
            Masked array of shape (n_thresholds, n_scorers) holding the
            scores for each scorer on each threshold for one fold of
            test data.

        TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER : MaskedHolderType
            Masked array of shape (n_thresholds, n_scorers) holding the
            times to score each scorer on each threshold for one fold of
            test data.

    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_FIT_OUTPUT_TUPLE, tuple)
    assert isinstance(_f_idx, int)
    assert isinstance(_SCORER_DICT, dict)
    assert all(map(callable, _SCORER_DICT.values()))
    assert isinstance(_THRESHOLDS, list)
    assert isinstance(_verbose, numbers.Real)
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *

    if _verbose >= 5:
        print(f"Start scoring fold {_f_idx + 1} test with different thresholds "
              f"and scorers")

    _estimator_, _fit_time, _fit_excepted = _FIT_OUTPUT_TUPLE

    TEST_THRESHOLD_x_SCORER__SCORE_LAYER: MaskedHolderType = \
        np.ma.zeros((len(_THRESHOLDS), len(_SCORER_DICT)), dtype=np.float64)
    TEST_THRESHOLD_x_SCORER__SCORE_LAYER.mask = True

    TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER: MaskedHolderType = \
        np.ma.zeros((len(_THRESHOLDS), len(_SCORER_DICT)), dtype=np.float64)
    TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER.mask = True

    # IF A FOLD EXCEPTED DURING FIT, ALL THE THRESHOLDS AND SCORERS
    # IN THAT FOLD LAYER GET SET TO error_score.
    # SCORE TIME CANT BE TAKEN SINCE SCORING WONT BE DONE SO ALSO MASK THAT
    if _fit_excepted:
        TEST_THRESHOLD_x_SCORER__SCORE_LAYER[:, :] = _error_score
        if _error_score is np.nan:
            TEST_THRESHOLD_x_SCORER__SCORE_LAYER[:, :] = np.ma.masked

        TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER[:, :] = np.nan
        TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER[:, :] = np.ma.masked

        if _verbose >= 5:
            print(f'fold {_f_idx + 1} excepted during fit, unable to score')

        return (TEST_THRESHOLD_x_SCORER__SCORE_LAYER,
                    TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER)

    # v v v only accessible if fit() did not except v v v

    _X_test = _X_test.persist()
    _y_test = _y_test.persist()

    pp0_time = time.perf_counter()
    _predict_proba = _estimator_.predict_proba(_X_test)[:, -1].ravel()
    _val_predict_proba(
        _predict_proba,
        _X_test.shape[0] if hasattr(_X_test, 'shape') else len(_X_test)
    )
    pp_time = time.perf_counter() - pp0_time
    del pp0_time

    if _verbose >= 5:
        print(f'fold {_f_idx + 1} test predict_proba time = {pp_time: ,.3g} s')
    del pp_time

    # GET SCORES FOR ALL SCORERS & THRESHOLDS ##########################

    _test_fold_score_t0 = time.perf_counter()
    for thresh_idx, _threshold in enumerate(_THRESHOLDS):

        _y_pred_t0 = time.perf_counter()
        _y_test_pred = (_predict_proba >= _threshold).astype(np.uint8)
        _ypt = time.perf_counter() - _y_pred_t0
        del _y_pred_t0
        if _verbose == 10:
            print(f"fold {_f_idx+1} test thresholding time = {_ypt: ,.3g} s")
        del _ypt

        for s_idx, scorer_key in enumerate(_SCORER_DICT):









            test_scorer_t0 = time.perf_counter()
            _score = _SCORER_DICT[scorer_key](_y_test, _y_test_pred)
            test_scorer_score_time = time.perf_counter() - test_scorer_t0
            del test_scorer_t0
            TEST_THRESHOLD_x_SCORER__SCORE_LAYER[thresh_idx, s_idx] = _score
            TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER[thresh_idx, s_idx] = \
                test_scorer_score_time

            if _verbose >= 8:
                print(f"fold {_f_idx + 1} '{scorer_key}' test score time = "
                      f"{test_scorer_score_time: ,.3g} s")

        del _score, test_scorer_score_time


    tfst = time.perf_counter() - _test_fold_score_t0
    del _test_fold_score_t0

    # END GET SCORE FOR ALL SCORERS & THRESHOLDS #######################

    if _verbose >= 5:
        print(f'End scoring fold {_f_idx + 1} test with different thresholds and '
              f'scorers')
        _ = _f_idx + 1

        print(f'fold {_} total test thresh & score wall time = {tfst: ,.3g} s')
        _ast = tfst / len(_SCORER_DICT) / len(_THRESHOLDS)
        print(f'fold {_} avg test thresh & score wall time = {_ast: ,.3g} s')
        del _ast

        __ = TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER
        print(f'fold {_} total test actual scoring time = {__.sum(): ,.3g} s')
        print(f'fold {_} avg test actual scoring time = {__.mean(): ,.3g} s')
        del _, __

    del _X_test, _y_test, _predict_proba, _y_test_pred, tfst


    return (TEST_THRESHOLD_x_SCORER__SCORE_LAYER,
                TEST_THRESHOLD_x_SCORER__SCORE_TIME_LAYER)



