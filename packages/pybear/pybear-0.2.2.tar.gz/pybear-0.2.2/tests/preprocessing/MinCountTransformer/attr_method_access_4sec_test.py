# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np
import pandas as pd
import polars as pl

from pybear.base import is_fitted
from pybear.base.exceptions import NotFittedError

from pybear.preprocessing import MinCountTransformer as MCT


bypass = False



# ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM FOR 1 & 2 RECURSION
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestAttrAccessBeforeAndAfterFitAndTransform:

    # simultaneously test 1 & 2 RCR
    # keep the different containers to test for feature_names_in_
    @pytest.mark.parametrize('x_format', ('np', 'pd', 'pl', 'bsr_array'))
    def test_attr_access(
        self, _X_factory, y_np, _columns, _kwargs, _shape, x_format
    ):

        _attrs = [
            'n_features_in_',
            'feature_names_in_',
            'original_dtypes_',
            'total_counts_by_column_',
            'instructions_'
        ]

        _X_wip = _X_factory(
            _format=x_format,
            _has_nan=False,
            _dtype='int',
            _dupl=None,
            _columns=_columns,
            _constants=None,
            _shape=_shape
        )

        if x_format == 'pd':
            _y_wip = pd.DataFrame(data=y_np, columns=['y'])
        elif x_format == 'pl':
            _y_wip = pl.from_numpy(data=y_np, schema=['y'])
        else:
            _y_wip = y_np

        OneRcrTestCls = MCT(**_kwargs)
        OneRcrTestCls.set_params(max_recursions=1, count_threshold=3)

        TwoRcrTestCls = MCT(**_kwargs)
        TwoRcrTestCls.set_params(max_recursions=2, count_threshold=3)

        # BEFORE FIT ***************************************************

        # ALL OF THESE SHOULD GIVE AttributeError/NotFittedError
        # MCT external attrs are @property and raise NotFittedError
        # which is child of AttrError
        # n_features_in_ & feature_names_in_ dont exist before fit.
        # @property cannot be set.
        for attr in _attrs:
            if attr in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    getattr(OneRcrTestCls, attr)
                with pytest.raises(AttributeError):
                    getattr(TwoRcrTestCls, attr)
            else:
                with pytest.raises(NotFittedError):
                    getattr(OneRcrTestCls, attr)
                with pytest.raises(NotFittedError):
                    getattr(TwoRcrTestCls, attr)

            if attr not in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    setattr(OneRcrTestCls, attr, any)
                with pytest.raises(AttributeError):
                    setattr(TwoRcrTestCls, attr, any)
        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        # TwoRcrTestCls cant be tested here, can only do fit_transform
        OneRcrTestCls.fit(_X_wip, _y_wip)

        # all attrs should be accessible after fit, the only exception
        # should be feature_names_in_ if not pd/pl
        # @property cannot be set.
        for attr in _attrs:
            try:
                out = getattr(OneRcrTestCls, attr)
                if attr == 'feature_names_in_':
                    if x_format in ['pd', 'pl']:
                        assert np.array_equiv(out, _columns), \
                            f"{attr} after fit() != originally passed columns"
                    else:
                        raise AssertionError(
                            f"{x_format} allowed access to 'feature_names_in_"
                        )
                elif attr == 'n_features_in_':
                    assert out == _shape[1]
                else:
                    # not validating accuracy of other module specific outputs
                    pass

            except Exception as e:
                if attr == 'feature_names_in_' and x_format not in ['pd', 'pl']:
                    assert isinstance(e, AttributeError)
                else:
                    raise AssertionError(
                        f"unexpected exception accessing {attr} after "
                        f"fit, x_format == {x_format} --- {e}"
                    )

        for attr in _attrs:
            if attr not in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    setattr(OneRcrTestCls, attr, any)
                with pytest.raises(AttributeError):
                    setattr(TwoRcrTestCls, attr, any)

        # END AFTER FIT ************************************************

        # AFTER TRANSFORM **********************************************

        OneRcrTestCls.transform(_X_wip)
        TwoRcrTestCls.fit_transform(_X_wip)

        # after transform, should be the exact same condition as after
        # fit, and pass the same tests
        # @property cannot be set.
        for attr in _attrs:
            try:
                out1 = getattr(OneRcrTestCls, attr)
                out2 = getattr(TwoRcrTestCls, attr)
                if attr == 'feature_names_in_':
                    if x_format in ['pd', 'pl']:
                        assert np.array_equiv(out1, _columns)
                        assert np.array_equiv(out2, _columns)
                    else:
                        raise AssertionError(
                            f"{x_format} allowed access to 'feature_names_in_"
                        )
                elif attr == 'n_features_in_':
                    assert out1 == _shape[1]
                    assert out2 == _shape[1]
                else:
                    # not validating accuracy of other module specific outputs
                    pass

            except Exception as e:
                if attr == 'feature_names_in_' and x_format not in ['pd', 'pl']:
                    assert isinstance(e, AttributeError)
                else:
                    raise AssertionError(
                        f"unexpected exception accessing {attr} after "
                        f"fit, x_format == {x_format} --- {e}"
                    )

        for attr in _attrs:
            if attr not in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    setattr(OneRcrTestCls, attr, any)
                with pytest.raises(AttributeError):
                    setattr(TwoRcrTestCls, attr, any)

        # END AFTER TRANSFORM ******************************************

# END ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM FOR 1 & 2 RECURSION


# ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM FOR 1 & 2RECURSION
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestMethodAccessBeforeAndAfterFitAndTransform:


    # _methods():
    # [
    #     'fit',
    #     'fit_transform',
    #     'get_feature_names_out',
    #     'get_metadata_routing',
    #     'get_params',
    #     'get_row_support',
    #     'get_support',
    #     'partial_fit',
    #     'print_instructions',
    #     'reset',
    #     'score',
    #     'set_output',
    #     'set_params',
    #     'transform'
    # ]


    # simultaneously test 1RCR & 2RCR
    def test_access_methods_before_fit(self, X_np, y_np, _kwargs):

        OneRcrTestCls = MCT(**_kwargs)
        OneRcrTestCls.set_params(max_recursions=1, count_threshold=3)

        TwoRcrTestCls = MCT(**_kwargs)
        TwoRcrTestCls.set_params(max_recursions=2, count_threshold=3)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(OneRcrTestCls.fit(X_np, y_np), MCT)
        with pytest.raises(ValueError):
            assert isinstance(TwoRcrTestCls.fit(X_np, y_np), MCT)

        # HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^v^v^
        # Reset changes is_fitted To False:
        # fit an instance  (done above)
        # assert the instance is fitted
        assert is_fitted(OneRcrTestCls) is True
        assert is_fitted(TwoRcrTestCls) is False
        # call :meth: reset
        OneRcrTestCls.reset()
        TwoRcrTestCls.reset()
        # assert the instance is not fitted
        assert is_fitted(OneRcrTestCls) is False
        assert is_fitted(TwoRcrTestCls) is False
        # END HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^

        # fit_transform()
        assert isinstance(OneRcrTestCls.fit_transform(X_np, y_np), tuple)
        assert isinstance(OneRcrTestCls.fit_transform(X_np ), np.ndarray)
        assert isinstance(TwoRcrTestCls.fit_transform(X_np, y_np), tuple)
        assert isinstance(TwoRcrTestCls.fit_transform(X_np ), np.ndarray)


        OneRcrTestCls.reset()
        TwoRcrTestCls.reset()

        # get_feature_names_out()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.get_feature_names_out(None)
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.get_feature_names_out(None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            OneRcrTestCls.get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TwoRcrTestCls.get_metadata_routing()

        # get_params()
        out1 = OneRcrTestCls.get_params(True)
        out2 = TwoRcrTestCls.get_params(True)
        assert isinstance(out1, dict)
        assert isinstance(out2, dict)
        del out1['max_recursions']
        del out2['max_recursions']
        assert out1 == out2, (f"pre-fit 1 recursion instance get_params() != "
                         f"get_params() from 2 recursion instance")
        del out1, out2

        # get_row_support()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.get_row_support(True)
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.get_row_support(True)

        # get_support()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.get_support(True)
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.get_support(True)

        # inverse_transform() - MCT should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(OneRcrTestCls, 'inverse_transform')
        with pytest.raises(AttributeError):
            getattr(TwoRcrTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(OneRcrTestCls.partial_fit(X_np, y_np), MCT)
        with pytest.raises(ValueError):
            assert isinstance(TwoRcrTestCls.partial_fit(X_np, y_np), MCT)

        # reset()
        assert isinstance(OneRcrTestCls.reset(), MCT)
        assert isinstance(TwoRcrTestCls.reset(), MCT)

        # print_instructions()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.print_instructions()
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.print_instructions()

        # score()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.score(X_np, y_np)
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.score(X_np, y_np)

        # set_output()
        assert isinstance(OneRcrTestCls.set_output(transform='pandas'), MCT)
        assert isinstance(TwoRcrTestCls.set_output(transform='pandas'), MCT)

        # set_params()
        # not fitted, there are no blocks for 2+ rcr or ic/hab callable
        OneRcrTestCls.set_params(handle_as_bool=[2, 3])
        TwoRcrTestCls.set_params(handle_as_bool=[2, 3])
        assert np.array_equal(OneRcrTestCls.handle_as_bool, [2, 3])
        assert np.array_equal(TwoRcrTestCls.handle_as_bool, [2, 3])
        OneRcrTestCls.set_params(ignore_columns=[0, 1])
        TwoRcrTestCls.set_params(ignore_columns=[0, 1])
        assert np.array_equal(OneRcrTestCls.ignore_columns, [0, 1])
        assert np.array_equal(TwoRcrTestCls.ignore_columns, [0, 1])
        OneRcrTestCls.set_params(max_recursions=2)
        TwoRcrTestCls.set_params(max_recursions=1)
        assert OneRcrTestCls.max_recursions == 2
        assert TwoRcrTestCls.max_recursions == 1
        OneRcrTestCls.set_params(max_recursions=1)
        TwoRcrTestCls.set_params(max_recursions=2)
        assert OneRcrTestCls.max_recursions == 1
        assert TwoRcrTestCls.max_recursions == 2

        # transform()
        with pytest.raises(NotFittedError):
            OneRcrTestCls.transform(X_np, y_np)
        with pytest.raises(NotFittedError):
            TwoRcrTestCls.transform(X_np, y_np)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    # 2 RCR cant be tested here, can only do fit_transform
    def test_access_methods_after_fit(self, X_np, y_np, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = MCT(**_kwargs)
        TestCls.fit(X_np, y_np)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(X_np), np.ndarray)

        TestCls.reset()

        # fit()
        assert isinstance(TestCls.fit(X_np), MCT)

        # get_feature_names_out()
        assert isinstance(TestCls.get_feature_names_out(None), np.ndarray)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        assert isinstance(TestCls.get_params(True), dict)

        # get_row_support()
        # not available until after transform()
        with pytest.raises(AttributeError):
            TestCls.get_row_support(False)

        # get_support()
        assert isinstance(TestCls.get_support(indices=True), np.ndarray)
        assert isinstance(TestCls.get_support(indices=False), np.ndarray)

        # inverse_transform()
        # MCT should never have inverse_transform method
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(X_np), MCT)

        # reset()
        assert isinstance(TestCls.reset(), MCT)

        TestCls.fit(X_np, y_np)

        # ** print_instructions()
        assert TestCls.print_instructions() is None

        # score()
        assert TestCls.score(X_np, y_np) is None

        # set_output()
        assert isinstance(TestCls.set_output(transform='default'), MCT)

        # set_params()
        # fitted, ic/hab callable blocked, max_recursions blocked
        with pytest.warns():
            TestCls.set_params(handle_as_bool=lambda X: [0])
        with pytest.warns():
            TestCls.set_params(ignore_columns=lambda X: [0])
        TestCls.set_params(count_threshold=3)
        TestCls.reset()
        assert isinstance(TestCls.set_params(max_recursions=2), MCT)
        # all params blocked if 2+ rcr
        assert TestCls.max_recursions == 2
        TestCls.fit_transform(X_np)
        with pytest.raises(ValueError):
            TestCls.set_params(count_threshold=5)
        with pytest.raises(ValueError):
            TestCls.set_params(max_recursions=1)
        TestCls.reset()
        TestCls.set_params(max_recursions=1)
        TestCls.fit(X_np)

        # transform()
        assert isinstance(TestCls.transform(X_np), np.ndarray)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    # simultaneously test 1 & 2 RCR
    def test_access_methods_after_transform(self, X_np, y_np, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        OneRcrTestCls = MCT(**_kwargs)
        OneRcrTestCls.set_params(max_recursions=1, count_threshold=3)
        TransformedTwoRcrTestCls = MCT(**_kwargs)
        TransformedTwoRcrTestCls.set_params(max_recursions=2, count_threshold=3)
        TransformedOneRcrTestCls = OneRcrTestCls.fit(X_np, y_np)
        TransformedOneRcrTestCls.transform(X_np, y_np)
        TransformedTwoRcrTestCls.fit_transform(X_np, y_np)

        # fit_transform()
        assert isinstance(TransformedOneRcrTestCls.fit_transform(X_np), np.ndarray)
        assert isinstance(TransformedTwoRcrTestCls.fit_transform(X_np), np.ndarray)

        # fit()
        assert isinstance(TransformedOneRcrTestCls.fit(X_np), MCT)
        TransformedOneRcrTestCls.transform(X_np)
        # cant test this for 2 RCR

        # get_feature_names_out()
        assert isinstance(
            TransformedOneRcrTestCls.get_feature_names_out(None),
            np.ndarray
        )
        assert isinstance(
            TransformedTwoRcrTestCls.get_feature_names_out(None),
            np.ndarray
        )

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedOneRcrTestCls.get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTwoRcrTestCls.get_metadata_routing()

        # get_params()
        out0 = OneRcrTestCls.get_params(True)
        out1 = TransformedOneRcrTestCls.get_params(True)
        out2 = TransformedTwoRcrTestCls.get_params(True)
        assert out1 == out0
        # ALL PARAMS SHOULD BE THE SAME EXCEPT FOR max_recursions
        del out1['max_recursions']
        del out2['max_recursions']
        assert out2 == out1
        del out0, out1, out2

        # get_row_support()
        for _indices in [True, False]:
            assert isinstance(
                TransformedOneRcrTestCls.get_row_support(_indices),
                np.ndarray
            )
            assert isinstance(
                TransformedTwoRcrTestCls.get_row_support(_indices),
                np.ndarray
            )

        # get_support()
        for _indices in [True, False]:
            assert isinstance(
                TransformedOneRcrTestCls.get_support(_indices),
                np.ndarray
            )
            assert isinstance(
                TransformedTwoRcrTestCls.get_support(_indices),
                np.ndarray
            )

        # inverse_transform()
        # MCT should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedOneRcrTestCls, 'inverse_transform')
        with pytest.raises(AttributeError):
            getattr(TransformedTwoRcrTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedOneRcrTestCls.partial_fit(X_np), MCT)
        TransformedOneRcrTestCls.transform(X_np)
        with pytest.raises(ValueError):
            TransformedTwoRcrTestCls.partial_fit(X_np)

        # ** print_instructions()
        # SHOULD BE THE SAME AS AFTER FIT, params WERE NOT CHANGED
        assert TransformedOneRcrTestCls.print_instructions() is None
        assert TransformedTwoRcrTestCls.print_instructions() is None

        # ** reset()
        assert isinstance(TransformedOneRcrTestCls.reset(), MCT)
        TransformedOneRcrTestCls.fit_transform(X_np)
        assert isinstance(TransformedTwoRcrTestCls.reset(), MCT)
        TransformedTwoRcrTestCls.fit_transform(X_np)

        # set_output()
        assert isinstance(
            TransformedOneRcrTestCls.set_output(transform='default'),
            MCT
        )
        assert isinstance(
            TransformedTwoRcrTestCls.set_output(transform='default'),
            MCT
        )

        # set_params()
        # 1 Rcr fitted & transformed, ic/hab fxn blocked, max_recursions blocked
        with pytest.warns():
            TransformedOneRcrTestCls.set_params(handle_as_bool=lambda X: [0])
        with pytest.warns():
            TransformedOneRcrTestCls.set_params(ignore_columns=lambda X: [0])
        with pytest.warns():
            TransformedOneRcrTestCls.set_params(max_recursions=2)
        TransformedOneRcrTestCls.set_params(count_threshold=5)
        assert TransformedOneRcrTestCls.count_threshold == 5
        TransformedOneRcrTestCls.set_params(count_threshold=3)
        assert TransformedOneRcrTestCls.count_threshold == 3

        with pytest.raises(ValueError):
            TransformedTwoRcrTestCls.set_params(count_threshold=5)
        with pytest.raises(ValueError):
            TransformedTwoRcrTestCls.set_params(max_recursions=1)
        with pytest.raises(ValueError):
            TransformedTwoRcrTestCls.set_params(ignore_columns=lambda x: [0, 1])

        # transform()
        assert isinstance(TransformedOneRcrTestCls.fit_transform(X_np), np.ndarray)
        with pytest.raises(ValueError):
            TransformedTwoRcrTestCls.transform(X_np)

        del OneRcrTestCls, TransformedOneRcrTestCls, TransformedTwoRcrTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM, 1 & 2 RECURSION




