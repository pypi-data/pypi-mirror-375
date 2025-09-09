# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.model_selection.GSTCV._type_aliases import (
    ScorerWIPType,
    ClassifierProtocol,
    MaskedHolderType,
    NDArrayHolderType
)
from .._type_aliases import (
    DaskXType,
    DaskYType
)

import numbers
import time

import numpy as np

from pybear.model_selection.GSTCV._GSTCVMixin._validation._predict_proba import _val_predict_proba



def _parallelized_train_scorer(
    _X_train: DaskXType,
    _y_train: DaskYType,
    _FIT_OUTPUT_TUPLE: tuple[ClassifierProtocol, float, bool],
    _f_idx: int,
    _SCORER_DICT: ScorerWIPType,
    _BEST_THRESHOLDS_BY_SCORER: NDArrayHolderType,
    _error_score: numbers.Real | None,
    _verbose: int
) -> MaskedHolderType:

    # dont adjust the spacing, is congruent with test scorer

    """Using the estimators fit on each train fold, use `predict_proba`
    and _X_trains to generate _y_preds and score against the corresponding
    _y_trains using all of the scorers.

    Fill one layer of the TRAIN_FOLD_x_SCORER__SCORE.

    Parameters
    ----------
    _X_train : DaskXType
        A train partition of the data that was fit.
    _y_train : DaskYType
        The corresponding train partition of the target for the X train
        partition.
    _FIT_OUTPUT_TUPLE : tuple[ClassifierProtocol, float, bool]
        A tuple holding the fitted estimator, the fit time (not needed
        here), and the fit_excepted boolean (needed here.)
    _f_idx : int
        The zero-based split index of the train partition used here;
        parallelism occurs over the different splits.
    _SCORER_DICT : ScorerWIPType
        A dictionary with scorer name as keys and the scorer callables
        as values. The scorer callables are scoring metrics (or similar),
        not make_scorer.
    _BEST_THRESHOLDS_BY_SCORER : NDArrayHolderType:
        After all of the fold / threshold / scorer combinations are
        scored, the folds are averaged and the threshold with the maximum
        score for each scorer is found. This vector has length n_scorers
        and in each position holds a float indicating the threshold
        value that is the best threshold for that scorer.
    _error_score : numbers.Real | Literal['raise']
        If this training fold excepted during fitting and `error_score`
        was set to the 'raise' literal, this module cannot be reached.
        Otherwise, a number or number-like was passed to `error_score`.
        If 'fit_excepted' is True, this module puts the `error_score`
        value in every position of the TRAIN_SCORER__SCORE_LAYER vector.
        If `error_score` is set to np.nan, that layer is also masked.
    _verbose : int
        A number from 0 to 10 that indicates the amount of information
        to display to the screen during the grid search process. 0 means
        no output, 10 means maximum output.

    Returns
    -------
    TRAIN_SCORER__SCORE_LAYER : MaskedHolderType
        Masked array of shape (n_scorers, ). The score for this fold of
        train data using every scorer and the best threshold associated
        with that scorer.










    """

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *
    assert isinstance(_FIT_OUTPUT_TUPLE, tuple)
    assert isinstance(_f_idx, int)
    assert isinstance(_SCORER_DICT, dict)
    assert all(map(callable, _SCORER_DICT.values()))
    assert isinstance(_BEST_THRESHOLDS_BY_SCORER, np.ndarray)
    assert isinstance(_verbose, numbers.Real)
    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * *

    if _verbose >= 5:
        print(f"Start scoring fold {_f_idx + 1} train with different scorers")


    _estimator_, _fit_time, _fit_excepted = _FIT_OUTPUT_TUPLE

    TRAIN_SCORER__SCORE_LAYER: MaskedHolderType = \
        np.ma.zeros(len(_SCORER_DICT), dtype=np.float64)
    TRAIN_SCORER__SCORE_LAYER.mask = True






    # IF A FOLD EXCEPTED DURING FIT, PUT IN error_score.
    # IF error_score==np.nan, ALSO MASK THIS LAYER
    if _fit_excepted:
        TRAIN_SCORER__SCORE_LAYER[:] = _error_score
        if _error_score is np.nan:
            TRAIN_SCORER__SCORE_LAYER[:] = np.ma.masked




        if _verbose >= 5:
            print(f'fold {_f_idx + 1} excepted during fit, unable to score')

        return TRAIN_SCORER__SCORE_LAYER


    # v v v only accessible if fit() did not except v v v

    _X_train = _X_train.persist()
    _y_train = _y_train.persist()

    pp0_time = time.perf_counter()
    _predict_proba = _estimator_.predict_proba(_X_train)[:, -1].ravel()
    _val_predict_proba(
        _predict_proba,
        _X_train.shape[0] if hasattr(_X_train, 'shape') else len(_X_train)
    )
    pp_time = time.perf_counter() - pp0_time
    del pp0_time

    if _verbose >= 5:
        print(f'fold {_f_idx + 1} train predict_proba time = {pp_time: ,.3g} s')
    del pp_time

    # GET SCORES FOR ALL SCORERS #######################################

    _train_fold_score_t0 = time.perf_counter()










    for s_idx, scorer_key in enumerate(_SCORER_DICT):

        _y_pred_t0 = time.perf_counter()
        _y_train_pred = (_predict_proba >= _BEST_THRESHOLDS_BY_SCORER[s_idx])
        _ypt = time.perf_counter() - _y_pred_t0
        del _y_pred_t0
        if _verbose == 10:
            print(f"fold {_f_idx+1} train thresholding time = {_ypt: ,.3g} s")
        del _ypt

        train_scorer_t0 = time.perf_counter()
        _score = _SCORER_DICT[scorer_key](_y_train, _y_train_pred)
        train_scorer_score_time = time.perf_counter() - train_scorer_t0
        del train_scorer_t0


        TRAIN_SCORER__SCORE_LAYER[s_idx] = _score

        if _verbose >= 8:
            print(f"fold {_f_idx+1} '{scorer_key}' train score time = "
                  f"{train_scorer_score_time: ,.3g} s")

        del _score, train_scorer_score_time


    tfst = time.perf_counter() - _train_fold_score_t0
    del _train_fold_score_t0

    # END GET SCORE FOR ALL SCORERS ####################################

    if _verbose >= 5:
        print(f'End scoring fold {_f_idx + 1} train with different scorers')

        _ = _f_idx + 1

        print(f'fold {_} total train thresh & score wall time = {tfst: ,.3g} s')
        _ast = tfst / len(_SCORER_DICT)
        print(f'fold {_} avg train thresh & score wall time = {_ast: ,.3g} s')
        del _ast






    del _X_train, _y_train, _predict_proba, _y_train_pred, tfst


    return TRAIN_SCORER__SCORE_LAYER





