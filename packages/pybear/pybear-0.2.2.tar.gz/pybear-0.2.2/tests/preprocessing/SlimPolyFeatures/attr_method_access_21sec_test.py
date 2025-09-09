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

from pybear.preprocessing import SlimPolyFeatures as SPF


bypass = False


# ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestAttrAccessBeforeAndAfterFitAndTransform:


    # keep the different containers to test for feature_names_in_
    @pytest.mark.parametrize('x_format', ('np', 'pd', 'pl', 'dia_matrix'))
    def test_attr_access(
        self, _X_factory, y_np, _columns, _kwargs, _shape, x_format
    ):

        _attrs = [
            'n_features_in_',
            'feature_names_in_',
            'poly_combinations_',
            'poly_duplicates_',
            'dropped_poly_duplicates_',
            'kept_poly_duplicates_',
            'poly_constants_'
        ]

        _X_wip = _X_factory(
            _format=x_format,
            _has_nan=False,
            _dtype='flt',
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

        TestCls = SPF(**_kwargs)

        # BEFORE FIT ***************************************************

        # ALL OF THESE SHOULD GIVE AttributeError/NotFittedError
        # SPF external attrs are @property and raise NotFittedError
        # which is child of AttrError
        # n_features_in_ & feature_names_in_ dont exist before fit.
        # @property cannot be set.
        for attr in _attrs:
            if attr in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    getattr(TestCls, attr)
            else:
                with pytest.raises(NotFittedError):
                    getattr(TestCls, attr)

            if attr not in ['n_features_in_', 'feature_names_in_']:
                with pytest.raises(AttributeError):
                    setattr(TestCls, attr, any)

        # END BEFORE FIT ***********************************************

        # AFTER FIT ****************************************************

        TestCls.fit(_X_wip, _y_wip)

        # all attrs should be accessible after fit, the only exception
        # should be feature_names_in_ if not pd/pl
        # @property cannot be set.
        for attr in _attrs:
            try:
                out = getattr(TestCls, attr)
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
                    setattr(TestCls, attr, any)

        # END AFTER FIT ************************************************

        # AFTER TRANSFORM **********************************************

        TestCls.transform(_X_wip)

        # after transform, should be the exact same condition as after
        # fit, and pass the same tests
        # @property cannot be set.
        for attr in _attrs:
            try:
                out = getattr(TestCls, attr)
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
                    setattr(TestCls, attr, any)

        # END AFTER TRANSFORM ******************************************

# END ACCESS ATTR BEFORE AND AFTER FIT AND TRANSFORM


# ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM ***
@pytest.mark.skipif(bypass is True, reason=f"bypass")
class TestMethodAccessBeforeAndAfterFitAndAfterTransform:


    # methods
    # [
    #     'fit',
    #     'fit_transform',
    #     'get_feature_names_out',
    #     'get_metadata_routing',
    #     'get_params',
    #     'partial_fit',
    #     'reset',
    #     'score',
    #     'set_output',
    #     'set_params',
    #     'transform'
    # ]


    def test_access_methods_before_fit(self, X_np, y_np, _kwargs):

        TestCls = SPF(**_kwargs)

        # **************************************************************
        # vvv BEFORE FIT vvv *******************************************

        # fit()
        assert isinstance(TestCls.fit(X_np, y_np), SPF)

        # HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^v^v^
        # Reset changes is_fitted To False:
        # fit an instance  (done above)
        # assert the instance is fitted
        assert is_fitted(TestCls) is True
        # call :meth: reset
        TestCls.reset()
        # assert the instance is not fitted
        assert is_fitted(TestCls) is False
        # END HERE IS A CONVENIENT PLACE TO TEST reset() ^v^v^v^v^v^v^v^

        # fit_transform()
        assert isinstance(TestCls.fit_transform(X_np, y_np), np.ndarray)

        TestCls.reset()

        # get_feature_names_out()
        with pytest.raises(NotFittedError):
            TestCls.get_feature_names_out(None)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        assert isinstance(TestCls.get_params(True), dict)

        # inverse_transform() - SPF should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(X_np, y_np), SPF)

        # reset()
        assert isinstance(TestCls.reset(), SPF)

        # score()
        with pytest.raises(NotFittedError):
            TestCls.score(X_np, y_np)

        # set_output()
        assert isinstance(TestCls.set_output(transform='pandas'), SPF)

        # set_params()
        assert isinstance(TestCls.set_params(keep='last'), SPF)
        assert TestCls.keep == 'last'

        # transform()
        with pytest.raises(NotFittedError):
            TestCls.transform(X_np)

        # END ^^^ BEFORE FIT ^^^ ***************************************
        # **************************************************************


    def test_access_methods_after_fit(self, X_np, y_np, _kwargs):

        # **************************************************************
        # vvv AFTER FIT vvv ********************************************

        TestCls = SPF(**_kwargs)
        TestCls.fit(X_np, y_np)

        # fit_transform()
        assert isinstance(TestCls.fit_transform(X_np), np.ndarray)

        TestCls.reset()

        # fit()
        assert isinstance(TestCls.fit(X_np), SPF)

        # get_feature_names_out()
        assert isinstance(TestCls.get_feature_names_out(None), np.ndarray)

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TestCls.get_metadata_routing()

        # get_params()
        assert isinstance(TestCls.get_params(True), dict)

        # inverse_transform()
        # SPF should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TestCls.partial_fit(X_np), SPF)

        # reset()
        assert isinstance(TestCls.reset(), SPF)

        TestCls.fit(X_np, y_np)

        # score()
        assert TestCls.score(X_np, y_np) is None

        # set_output()
        assert isinstance(TestCls.set_output(transform='default'), SPF)

        # set_params()
        assert isinstance(TestCls.set_params(keep='random'), SPF)

        # transform()
        assert isinstance(TestCls.transform(X_np), np.ndarray)

        del TestCls

        # END ^^^ AFTER FIT ^^^ ****************************************
        # **************************************************************


    def test_access_methods_after_transform(self, X_np, y_np, _kwargs):

        # **************************************************************
        # vvv AFTER TRANSFORM vvv **************************************
        FittedTestCls = SPF(**_kwargs).fit(X_np, y_np)
        TransformedTestCls = SPF(**_kwargs).fit(X_np, y_np)
        TransformedTestCls.transform(X_np)

        # fit_transform()
        assert isinstance(TransformedTestCls.fit_transform(X_np), np.ndarray)

        # fit()
        assert isinstance(TransformedTestCls.fit(X_np), SPF)

        TransformedTestCls.transform(X_np)

        # get_feature_names_out()
        assert isinstance(
            TransformedTestCls.get_feature_names_out(None),
            np.ndarray
        )

        # get_metadata_routing()
        with pytest.raises(NotImplementedError):
            TransformedTestCls.get_metadata_routing()

        # get_params()
        assert TransformedTestCls.get_params(True) == \
                FittedTestCls.get_params(True), \
            f"get_params() after transform() != before transform()"

        # inverse_transform()
        # SPF should never have inverse_transform
        with pytest.raises(AttributeError):
            getattr(TransformedTestCls, 'inverse_transform')

        # partial_fit()
        assert isinstance(TransformedTestCls.partial_fit(X_np), SPF)

        # reset()
        assert isinstance(TransformedTestCls.reset(), SPF)
        TransformedTestCls.fit_transform(X_np)

        # set_output()
        assert isinstance(
            TransformedTestCls.set_output(transform='default'), SPF
        )

        # set_params()
        assert isinstance(TransformedTestCls.set_params(keep='first'), SPF)

        # transform()
        assert isinstance(TransformedTestCls.fit_transform(X_np), np.ndarray)

        del FittedTestCls, TransformedTestCls

        # END ^^^ AFTER TRANSFORM ^^^ **********************************
        # **************************************************************

# END ACCESS METHODS BEFORE AND AFTER FIT AND TRANSFORM




