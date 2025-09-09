# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest

import pandas as pd
import numpy as np
from dask import delayed
import dask.array as da
import dask.dataframe as ddf
import scipy.sparse as ss

from pybear_dask.base import is_classifier



from sklearn.linear_model import (
    LogisticRegression as sklearn_LogisticRegression,
    LinearRegression as sklearn_LinearRegression,
    PoissonRegressor as sklearn_PoissonRegressor,
    SGDClassifier as sklearn_SGDClassifier,
    SGDRegressor as sklearn_SGDRegressor
)
from sklearn.svm import SVC as sklearn_SVC
from sklearn.neural_network import (
    MLPClassifier as sklearn_MLPClassifier,
    MLPRegressor as sklearn_MLPRegressor
)
from sklearn.naive_bayes import GaussianNB as sklearn_GaussianNB
from sklearn.calibration import (
    CalibratedClassifierCV as sklearn_CalibratedClassifierCV
)


from dask_ml.linear_model import (
    LogisticRegression as dask_LogisticRegression,
    LinearRegression as dask_LinearRegression,
    PoissonRegression as dask_PoissonRegression
)
from dask_ml.ensemble import (
    BlockwiseVotingClassifier as BlockwiseVotingClassifier,
    BlockwiseVotingRegressor as BlockwiseVotingRegressor
)
from dask_ml.naive_bayes import GaussianNB as dask_GaussianNB

# from lightgbm import (
#     LGBMClassifier,
#     LGBMRegressor,
#     LGBMRanker,
#     DaskLGBMClassifier,
#     DaskLGBMRegressor,
#     DaskLGBMRanker
# )

from sklearn.feature_extraction.text import (
    CountVectorizer as sklearn_CountVectorizer,
    CountVectorizer as dask_CountVectorizer
)

from sklearn.model_selection import (
    GridSearchCV as sklearn_GridSearchCV,
    RandomizedSearchCV as sklearn_RandomizedSearchCV
)
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import (
    HalvingGridSearchCV as sklearn_HalvingGridSearchCV,
    HalvingRandomSearchCV as sklearn_HalvingRandomSearchCV
)


from dask_ml.model_selection import (
    GridSearchCV as dask_GridSearchCV,
    RandomizedSearchCV as dask_RandomizedSearchCV,
    IncrementalSearchCV as dask_IncrementalSearchCV,
    HyperbandSearchCV as dask_HyperbandSearchCV,
    SuccessiveHalvingSearchCV as dask_SuccessiveHalvingSearchCV,
    InverseDecaySearchCV as dask_InverseDecaySearchCV
)

from sklearn.pipeline import Pipeline
from dask_ml.wrappers import Incremental, ParallelPostFit



# a = XGBClassifier
# b = XGBRegressor
c = sklearn_LinearRegression
d = sklearn_LogisticRegression
e = sklearn_PoissonRegressor
f = sklearn_SGDClassifier
g = sklearn_SGDRegressor
h = sklearn_SVC
i = sklearn_MLPClassifier
j = sklearn_MLPRegressor
k = sklearn_GaussianNB
l = dask_LinearRegression
m = dask_LogisticRegression
n = dask_PoissonRegression
o = BlockwiseVotingClassifier
p = BlockwiseVotingRegressor
q = dask_GaussianNB
# r = LGBMClassifier
# s = LGBMRegressor
# t = LGBMRanker
# u = DaskLGBMClassifier
# v = DaskLGBMRegressor
# x = DaskLGBMRanker
y = sklearn_CalibratedClassifierCV


# BUILD TRUTH TABLE FOR ALL ESTIMATORS IS/ISNT A CLASSIFIER ** ** ** ** ** ** **

ALL_ESTIMATORS = \
    [c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, y]

# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

def get_fxn_name(_module):
    try:
        fxn_name = type(_module()).__name__
    except:
        try:
            fxn_name = type(_module(sklearn_LogisticRegression())).__name__
        except:
            raise ValueError(
                f'get_fxn_name(): 'f'estimator "{_module}" wont initialize'
            )

    return fxn_name


ESTIMATOR_NAMES = [get_fxn_name(_) for _ in ALL_ESTIMATORS]

del get_fxn_name


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


STR_ESTIMATOR_PATHS = \
    np.fromiter((str(__).lower() for __ in ALL_ESTIMATORS), dtype='<U200')


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

NAMES = np.empty(len(ESTIMATOR_NAMES), dtype='<U200')

for idx, (str_estimator_path, estimator_name) in (
        enumerate(zip(STR_ESTIMATOR_PATHS, ESTIMATOR_NAMES))):
    if 'dask' in str_estimator_path:
        if 'lightgbm' in str_estimator_path:
            continue
        elif 'blockwisevotingclassifier' in str_estimator_path:
            continue
        elif 'blockwisevotingregressor' in str_estimator_path:
            continue
        else:
            NAMES[idx] = f'dask_{estimator_name}'



KEYS = np.empty(len(ESTIMATOR_NAMES))
for idx, (str_estimator_path, estimator_name) in \
        enumerate(zip(STR_ESTIMATOR_PATHS, ESTIMATOR_NAMES)):

    if any(
        [x in str_estimator_path for x in \
        ['lightgbm', 'xgb', 'blockwisevotingclassifier', 'blockwisevotingregressor']]
    ):
        prefix = ''
    elif 'sklearn' in str_estimator_path:
        if f'dask_{estimator_name}' in NAMES:
            prefix = 'sklearn_'
        elif f'PoissonRegressor' in estimator_name:
            prefix = 'sklearn_'
        else:
            prefix = ''
    elif 'dask' in str_estimator_path:
        pass
    else:
        raise ValueError(f"Logic getting package name from str(estimator) failed")

    if NAMES[idx][:5] == 'dask_':
        pass
    else:
        NAMES[idx] = prefix + estimator_name

    if 'classifier' in NAMES[idx].lower():
        KEYS[idx] = True
    elif 'logistic' in NAMES[idx].lower():
        KEYS[idx] = True
    elif 'svc' in NAMES[idx].lower():
        KEYS[idx] = True
    elif 'gaussiannb' in NAMES[idx].lower():
        KEYS[idx] = True
    else:
        KEYS[idx] = False


# ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

IS_CLF_LOOKUP = pd.DataFrame({'TRUTH': KEYS}, index=NAMES).astype({'TRUTH': bool})


# KEEP
# ALL_ESTIMATORS, NAMES, IS_CLF_LOOKUP


del ESTIMATOR_NAMES, STR_ESTIMATOR_PATHS, KEYS

# END BUILD TRUTH TABLE FOR ALL ESTIMATORS IS/ISNT A CLASSIFIER ** ** ** ** **




def pass_estimator_to_wrapper(_est_name, _estimator, TRUTH_TABLE):

    # WHEN USING is_classifier, THE ESTIMATOR CAN BE PASSED AS A CLASS OR AS AN
    # INSTANCE, SO DONT NEED TO PASS AS AN INSTANCE BUT WHEN PASSING ESTIMATOR
    # TO WRAPPERS (Pipeline, Incremental, ParallelPostFit), IT MUST BE AN
    # INSTANCE AND NOT THE CLASS ITSELF. SOME ESTIMATORS HAVE ARGS THAT IT MUST
    # TAKE, CAUSING EMPTY () TO EXCEPT, PARTICULARLY THE dask Blockwise. USE
    # THIS FUNCTION TO PASS KOSHER ARGS TO THE WRAPPER

    """
    :param: _est_name: str
    :param: _estimator: sklearn / dask / xgboost / lightgbm estimator
    :param:  TRUTH_TABLE: pd.DataFrame
    :return:
        new_est_name:str,
        new_est_fit_to_be_passed_to_wrapper: sklearn or dask estimator
    """

    try:
        _estimator()
        return f'{_est_name}()', _estimator()

    except:

        is_dask = 'dask' in _est_name
        is_clf = TRUTH_TABLE.loc[_est_name, 'TRUTH']

        if is_dask:
            dummy_classifier = dask_LogisticRegression
            dc_name = 'dask_LogisticRegression'
            dummy_non_classifier = dask_LinearRegression
            dnc_name = 'dask_LinearRegression'
        else:
            dummy_classifier = sklearn_LogisticRegression
            dc_name = 'sklearn_LogisticRegression'
            dummy_non_classifier = sklearn_LinearRegression
            dnc_name = 'sklearn_LinearRegression'

        try:
            if is_clf:
                inited_estimator = _estimator(dummy_classifier())
            else:
                inited_estimator = _estimator(dummy_non_classifier())

            new_est_name = f'{_est_name}({dc_name if is_clf else dnc_name}())'

            return new_est_name, inited_estimator

        except:
            raise Exception(
                f'get_fxn_name(): estimator "{_est_name}" wont initialize')


def build_pipeline(_est_name, inited_estimator):
    """
    :param: est_name: str
    :param: inited_estimator: sklearn / dask / xgboost / lightgbm estimator
    :return: pipline_name: str, pipeline: sklearn.pipeline.Pipeline
    """

    is_dask = 'dask' in _est_name

    if is_dask:
        _count_vectorizer = dask_CountVectorizer
        _ct_vec_name = 'dask_CountVectorizer'
    else:
        _count_vectorizer = sklearn_CountVectorizer
        _ct_vec_name = 'sklearn_CountVectorizer'

    try:
        _pipeline = Pipeline(
            steps=[
                (f'{_ct_vec_name}', _count_vectorizer()),
                (f'{_est_name}', inited_estimator)
            ]
        )

        return f'Pipeline({_ct_vec_name}(), {_est_name})', _pipeline

    except:
        raise Exception(f'Exception trying to build pipeline around {_est_name}')


def wrap_with_gscv(_est_name, _estimator, gscv_name, gscv):
    """
    :param: est_name: str
    :param: est: sklearn / dask / xgboost / lightgbm estimator
    :param: gscv_name: str
    :param: gscv_est: sklearn / dask grid search estimator
    :return: new_est_name: str, est_wrapped_in_gscv: sklearn / dask grid search estimator
    """

    if gscv_name is None:
        new_est_name, est_wrapped_in_gscv = _est_name, _estimator
    else:
        base_gscv_params = {'param_grid': {'C': np.logspace(-1, 1, 3)}}

        if gscv_name == 'sklearn_GridSearchCV':
            gscv_params = base_gscv_params
        elif gscv_name == 'sklearn_RandomizedSearchCV':
            gscv_params = {'param_distributions': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'sklearn_HalvingGridSearchCV':
            gscv_params = base_gscv_params
        elif gscv_name == 'sklearn_HalvingRandomSearchCV':
            gscv_params = {'param_distributions': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'dask_GridSearchCV':
            gscv_params = base_gscv_params
        elif gscv_name == 'dask_RandomizedSearchCV':
            gscv_params = {'param_distributions': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'dask_IncrementalSearchCV':
            gscv_params = {'parameters': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'dask_HyperbandSearchCV':
            gscv_params = {'parameters': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'dask_SuccessiveHalvingSearchCV':
            gscv_params = {'parameters': {'C': np.logspace(-1, 1, 3)}}
        elif gscv_name == 'dask_InverseDecaySearchCV':
            gscv_params = {'parameters': {'C': np.logspace(-1, 1, 3)}}
        else:
            raise Exception

        new_est_name = f"{gscv_name}({_est_name})"
        est_wrapped_in_gscv = gscv(_estimator, **gscv_params)

    return new_est_name, est_wrapped_in_gscv




GSCV_NAMES = [
    None, 'sklearn_GridSearchCV', 'sklearn_RandomizedSearchCV',
    'sklearn_HalvingGridSearchCV', 'sklearn_HalvingRandomSearchCV',
    'dask_GridSearchCV', 'dask_RandomizedSearchCV',
    'dask_IncrementalSearchCV', 'dask_HyperbandSearchCV',
    'dask_SuccessiveHalvingSearchCV', 'dask_InverseDecaySearchCV'
]

GSCVS = [
    None, sklearn_GridSearchCV, sklearn_RandomizedSearchCV,
    sklearn_HalvingGridSearchCV, sklearn_HalvingRandomSearchCV,
    dask_GridSearchCV, dask_RandomizedSearchCV,
    dask_IncrementalSearchCV, dask_HyperbandSearchCV,
    dask_SuccessiveHalvingSearchCV, dask_InverseDecaySearchCV
]



class TestGSCVSConformingEstimators:   # _estimator ACCEPTS EMPTY ()

    # TYPES = ['uninstantiated', 'instantiated', 'pipeline', 'incremental',
    #          'parallelpostfit', 'pipeline+incremental', 'pipeline+parallelpostfit',
    #          'incremental+pipeline', 'parallelpostfit+pipeline'
    #          ]


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_uninstantiated(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, feed_fxn = \
            wrap_with_gscv(_est_name, _estimator, gscv_name, gscv)

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_instantiated(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, feed_fxn = \
            wrap_with_gscv(new_est_name, inited_estimator, gscv_name, gscv)

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_pipeline(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, inited_pipeline = \
            build_pipeline(new_est_name, inited_estimator)
        new_est_name, feed_fxn = \
            wrap_with_gscv(new_est_name, inited_pipeline, gscv_name, gscv)

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_incremental(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, feed_fxn = \
            wrap_with_gscv(
                f'Incremental({new_est_name})',
                Incremental(inited_estimator),
                gscv_name,
                gscv
            )

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_parallelpostfit(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, feed_fxn = \
            wrap_with_gscv(
                f'ParallelPostFit({new_est_name})',
                ParallelPostFit(inited_estimator),
                gscv_name,
                gscv
            )

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_pipeline_incremental(self, _est_name, _estimator, gscv_name, gscv):
        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, inited_pipeline = \
            build_pipeline(
                f'Incremental({new_est_name})',
                Incremental(inited_estimator))
        new_est_name, feed_fxn = \
            wrap_with_gscv(new_est_name, inited_pipeline, gscv_name, gscv)
        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_pipeline_parallelpostfit(
        self, _est_name, _estimator, gscv_name, gscv
    ):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, inited_pipeline = \
            build_pipeline(f'ParallelPostFit({new_est_name})',
                           ParallelPostFit(inited_estimator))
        new_est_name, feed_fxn = \
            wrap_with_gscv(new_est_name, inited_pipeline, gscv_name, gscv)
        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_incremental_pipeline(self, _est_name, _estimator, gscv_name, gscv):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, inited_pipeline = \
            build_pipeline(new_est_name, inited_estimator)
        new_est_name, feed_fxn = \
            wrap_with_gscv(
                f'Incremental({new_est_name})',
                Incremental(inited_pipeline),
                gscv_name,
                gscv
        )

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    @pytest.mark.parametrize('_est_name, _estimator', zip(NAMES, ALL_ESTIMATORS))
    def test_parallelpostfit_pipeline(
        self, _est_name, _estimator, gscv_name, gscv
    ):

        new_est_name, inited_estimator = \
            pass_estimator_to_wrapper(_est_name, _estimator, IS_CLF_LOOKUP)
        new_est_name, inited_pipeline = \
            build_pipeline(new_est_name, inited_estimator)
        new_est_name, feed_fxn = \
            wrap_with_gscv(
            f'ParallelPostFit({new_est_name})',
            ParallelPostFit(inited_pipeline),
            gscv_name,
            gscv
        )

        assert IS_CLF_LOOKUP.loc[_est_name, 'TRUTH'] == is_classifier(feed_fxn)


class TestGSCVSNonConformingEstimators:  # _estimator DOES NOT ACCEPT EMPTY ()

    # NON-CONFORMING ESTIMATORS PASSED TO BlockwiseVotingClassifier,
    # BlockwiseVotingRegressor, CalibratedClassifierCV


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_bvc_class(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'BlockwiseVotingClassifier(sklearn_LinearRegression)',
            BlockwiseVotingClassifier(sklearn_LinearRegression),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is True


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_bvc_instance(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'BlockwiseVotingClassifier(sklearn_LinearRegression())',
            BlockwiseVotingClassifier(sklearn_LinearRegression()),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is True


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_bvr_class(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'BlockwiseVotingRegressor(sklearn_LogisticRegression)',
            BlockwiseVotingRegressor(sklearn_LogisticRegression),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is False


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_bvr_instance(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'BlockwiseVotingRegressor(sklearn_LogisticRegression())',
            BlockwiseVotingRegressor(sklearn_LogisticRegression()),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is False


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_cccv_class(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'CalibratedClassifierCV(sklearn_LinearRegression)',
            sklearn_CalibratedClassifierCV(sklearn_LinearRegression),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is True


    @pytest.mark.parametrize('gscv_name, gscv', zip(GSCV_NAMES, GSCVS))
    def test_cccv_instance(self, gscv_name, gscv):

        new_est_name, feed_fxn = wrap_with_gscv(
            'CalibratedClassifierCV(sklearn_LinearRegression())',
            sklearn_CalibratedClassifierCV(sklearn_LinearRegression()),
            gscv_name,
            gscv
        )

        assert is_classifier(feed_fxn) is True




class TestNonEstimators:

    def test_fails_string(self):
        assert is_classifier('some string') is False


    def test_fails_integer(self):
        assert is_classifier(3) is False


    def test_fails_float(self):
        assert is_classifier(np.pi) is False


    def test_fails_list(self):
        assert is_classifier(list(range(5))) is False


    def test_fails_set(self):
        assert is_classifier(set(range(5))) is False


    def test_fails_dictionary(self):
        assert is_classifier({'A': np.arange(5)}) is False


    def test_fails_numpy_array(self):
        assert is_classifier(np.random.randint(0,10,(20,10))) is False


    def test_fails_pandas_dataframe(self):

        DF = pd.DataFrame(
            data=np.random.randint(0,10,(20,5)),
            columns=list('abcde')
        )

        assert is_classifier(DF) is False


    def test_fails_coo_array(self):

        COO_ARRAY = ss.coo_array(np.random.randint(0,2,(100,50)))

        assert is_classifier(COO_ARRAY) is False


    def test_fails_lazy_dask_array(self):

        DA = da.random.randint(0,10,(20,5), chunks=(5,5))

        assert is_classifier(DA) is False


    def test_fails_computed_dask_array(self):

        DA = da.random.randint(0,10,(20,5), chunks=(5,5))

        assert is_classifier(DA.compute()) is False


    def test_fails_lazy_dask_dataframe(self):

        DDF = ddf.from_pandas(
            pd.DataFrame(
                data=da.random.randint(0,10,(20,5)),
                columns=list('abcde')
            ),
            npartitions=5,
        )

        assert is_classifier(DDF) is False


    def test_fails_computed_dask_dataframe(self):

        DDF = ddf.from_pandas(
            pd.DataFrame(
                data=da.random.randint(0,10,(20,5)),
                columns=list('abcde')
            ),
            npartitions=5,
        )

        assert is_classifier(DDF.compute()) is False


    def test_fails_lazy_dask_delayed(self):
        assert is_classifier(delayed([_ for _ in range(10)])) is False


    def test_fails_computed_dask_delayed(self):
        assert is_classifier(delayed([_ for _ in range(10)]).compute()) is False


    def test_fails_function(self):

        def test_function(a,b):
            return a + b

        assert is_classifier(test_function) is False


    def test_fails_lambda_function(self):
        assert is_classifier(lambda x: x + 1) is False


    def test_fails_class(self):

        class test_class:
            def __init__(self, a, b):
                self.a, self.b = a, b
            def fit(self, X, y):
                return X + y

        assert is_classifier(test_class) is False




