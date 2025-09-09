# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base.mixins._SetOutputMixin import SetOutputMixin
from pybear.base.mixins._FitTransformMixin import FitTransformMixin
from pybear.base.mixins._FeatureMixin import FeatureMixin

import uuid
import numpy as np
import pandas as pd
import scipy.sparse as ss
import polars as pl

import pytest



class TestSetOutputMixin:


    # fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    @staticmethod
    @pytest.fixture(scope='function')
    def _ClsTemplate():

        class Cls(FeatureMixin, FitTransformMixin, SetOutputMixin):


            def __init__(self, fill:bool=True):

                self._is_fitted = False
                self.fill = fill


            def __pybear_is_fitted__(self):
                return getattr(self, '_is_fitted', None) is True


            def reset(self):
                self._is_fitted = False

                return self


            def _validate(self, OBJ, name):
                if not isinstance(OBJ, (np.ndarray, pd.DataFrame)) \
                        and not hasattr(OBJ, 'toarray'):
                    raise TypeError(
                        f"'{name}' must be a numpy array, pandas dataframe, "
                        f"or scipy sparse matrix/array."
                    )


            def fit(self, X, y=None):

                self._validate(X, 'X')
                if y is not None:
                    self._validate(y, 'y')

                self.n_features_in_ = X.shape[1]

                if hasattr(X, 'columns'):
                    self.feature_names_in_ = np.array(X.columns, dtype=object)

                self.fill_value = np.random.randint(1, 10)

                self._is_fitted = True

                return self

        return Cls


    @staticmethod
    @pytest.fixture(scope='function')
    def _mock_transformer_1(_ClsTemplate):

        class Foo(_ClsTemplate):

            @SetOutputMixin._set_output_for_transform
            def transform(self, X):

                """
                Docstring sandbox trfm 1.

                """

                if not self._is_fitted:
                    raise ValueError(f"_mock_transformer must be fitted")

                self._validate(X, 'X')

                if self.fill:
                    X[(X != 0)] = self.fill_value

                return X

        return Foo


    @staticmethod
    @pytest.fixture(scope='function')
    def _mock_transformer_2(_ClsTemplate):

        class Foo(_ClsTemplate):

            @SetOutputMixin._set_output_for_transform
            def transform(self, X, copy=True):

                """
                Docstring sandbox trfm 2.

                """

                if not self._is_fitted:
                    raise ValueError(f"_mock_transformer must be fitted")

                assert isinstance(copy, bool)

                self._validate(X, 'X')

                if copy:
                    _X = X.copy()
                else:
                    _X = X

                if self.fill:
                    _X[(_X != 0)] = self.fill_value

                return _X

        return Foo


    @staticmethod
    @pytest.fixture(scope='function')
    def _mock_transformer_3(_ClsTemplate):

        class Foo(_ClsTemplate, FitTransformMixin, SetOutputMixin):

            @SetOutputMixin._set_output_for_transform
            def transform(self, X, y=None):   # need y here for MCT

                """
                Docstring sandbox trfm 3.

                """

                if not self._is_fitted:
                    raise ValueError(f"_mock_transformer must be fitted")

                self._validate(X, 'X')
                if y is not None:
                    self._validate(y, 'y')

                if self.fill:
                    X[(X != 0)] = self.fill_value

                if y is not None:
                    if self.fill:
                        y[(y != 0)] = self.fill_value
                    return X, y
                else:
                    return X

        return Foo



    @staticmethod
    @pytest.fixture(scope='function')
    def _mock_transformer_4(_ClsTemplate):

        class Foo(_ClsTemplate, FitTransformMixin, SetOutputMixin):

            @SetOutputMixin._set_output_for_transform
            def transform(self, X, y=None, copy=True): #need y here for MCT

                """
                Docstring sandbox trfm 3.

                """

                if not self._is_fitted:
                    raise ValueError(f"_mock_transformer must be fitted")

                assert isinstance(copy, bool)

                self._validate(X, 'X')
                if y is not None:
                    self._validate(y, 'y')

                if copy:
                    _X = X.copy()
                    _y = y.copy()
                else:
                    _X = X
                    _y = y

                if self.fill:
                    _X[(_X != 0)] = self.fill_value

                if y is not None:
                    if self.fill:
                        _y[(_y != 0)] = self.fill_value
                    return _X, _y
                else:
                    return _X

        return Foo

    # END fixtures ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    # set_output validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_transform',
        (-2.7, -1, 0, 1, 2.7, True, False, [0,1], (1,), {'a':1}, lambda x: x)
    )
    def test_set_output_rejects_junk(
        self, junk_transform, _mock_transformer_1, _X_np
    ):

        trfm = _mock_transformer_1()
        trfm.fit(_X_np)
        with pytest.raises(TypeError):
            trfm.set_output(transform=junk_transform)


    @pytest.mark.parametrize('bad_transform', ('eat', 'more', 'chikn'))
    def test_set_output_rejects_bad(
        self, bad_transform, _mock_transformer_1, _X_np
    ):

        trfm = _mock_transformer_1()
        trfm.fit(_X_np)
        with pytest.raises(ValueError):
            trfm.set_output(transform=bad_transform)


    @pytest.mark.parametrize('good_transform',
        ('default', 'pandas', 'polars', None)
    )
    def test_set_output_accepts_good(
        self, good_transform, _mock_transformer_1, _X_np
    ):

        trfm = _mock_transformer_1()
        trfm.fit(_X_np)
        trfm.set_output(transform=good_transform)

    # END set_output validation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # _set_output_for_transform validation -- -- -- -- -- -- -- -- -- -- -- -- --
    def test_set_output_for_transform_rejects_invalid_container_from_transform(
        self, _mock_transformer_1, _X_np
    ):

        _X = list(map(list, _X_np))

        trfm = _mock_transformer_1()
        trfm.fit(_X_np)
        trfm.set_output(transform='pandas')
        with pytest.raises(TypeError):
            trfm.transform(_X)

    # END _set_output_for_transform validation -- -- -- -- -- -- -- -- --


    # transform works without having called set_output -- -- -- -- -- -- -- --

    # _set_output_for_transform() will look for a '_output_transform' attr
    # in the child. but if :meth: set_output hasnt been called it wont
    # exist.  using getattr in _set_output_for_transform to get around this.

    def test_transform_works_without_output_transform_attr(
        self, _mock_transformer_1, _X_np
    ):

        trfm = _mock_transformer_1()
        trfm.fit(_X_np)
        # trfm.set_output('pandas')   <==== dont call this!
        trfm.transform(_X_np)

    # END transform works without having called set_output -- -- -- -- -- -- --


    @pytest.mark.parametrize('input_container', ['np', 'pd', 'csr', 'csc'])
    @pytest.mark.parametrize('output_container', ['default', 'pandas', 'polars', None])
    def test_container_accuracy_1(
        self, _X_np, _columns, _y_np, input_container, output_container,
        _mock_transformer_1
    ):

        if input_container == 'np':
            _X = _X_np
        elif input_container == 'pd':
            _X = pd.DataFrame(data=_X_np, columns=_columns)
        elif input_container == 'csr':
            _X = ss.csr_array(_X_np)
        elif input_container == 'csc':
            _X = ss.csc_array(_X_np)
        else:
            raise Exception

        _og_dtype = type(_X)

        # transformer 1 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
        trfm1 = _mock_transformer_1()
        trfm1.set_output(transform=output_container)
        trfm1.fit(_X)
        TRFM_X = trfm1.transform(_X)


        if output_container is None:
            assert isinstance(TRFM_X, _og_dtype)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'default':
            assert isinstance(TRFM_X, np.ndarray)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'pandas':
            assert isinstance(TRFM_X, pd.DataFrame)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'polars':
            assert isinstance(TRFM_X, pl.DataFrame)
            assert TRFM_X.shape == _X.shape
        else:
            raise Exception


        # assert equality, convert TRFM_X to np

        try: TRFM_X = TRFM_X.to_array()
        except: pass

        try: TRFM_X = TRFM_X.toarray()
        except: pass

        # remember that TRFM_X was filled with fill_value from trfm1
        assert np.array_equal(TRFM_X, np.full(TRFM_X.shape, trfm1.fill_value))

        # END transformer 1 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **



    @pytest.mark.parametrize('input_container', ['np', 'pd', 'csr', 'csc'])
    @pytest.mark.parametrize('output_container', ['default', 'pandas', 'polars', None])
    def test_container_accuracy_2(
        self, _X_np, _columns, _y_np, input_container, output_container,
        _mock_transformer_2
    ):

        if input_container == 'np':
            _X = _X_np
        elif input_container == 'pd':
            _X = pd.DataFrame(data=_X_np, columns=_columns)
        elif input_container == 'csr':
            _X = ss.csr_array(_X_np)
        elif input_container == 'csc':
            _X = ss.csc_array(_X_np)
        else:
            raise Exception

        _og_dtype = type(_X)

        # transformer 2 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        trfm2 = _mock_transformer_2()
        trfm2.set_output(transform=output_container)
        trfm2.fit(_X)
        TRFM_X = trfm2.transform(_X, copy=False)


        if output_container is None:
            assert isinstance(TRFM_X, _og_dtype)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'default':
            assert isinstance(TRFM_X, np.ndarray)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'pandas':
            assert isinstance(TRFM_X, pd.DataFrame)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'polars':
            assert isinstance(TRFM_X, pl.DataFrame)
            assert TRFM_X.shape == _X.shape
        else:
            raise Exception


        # assert equality, convert TRFM_X to np

        try: TRFM_X = TRFM_X.to_array()
        except: pass

        try: TRFM_X = TRFM_X.toarray()
        except: pass

        # remember that TRFM_X was filled with fill_value from trfm2
        assert np.array_equal(TRFM_X, np.full(TRFM_X.shape, trfm2.fill_value))

        # END transformer 2 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @pytest.mark.parametrize('input_container', ['np', 'pd', 'csr', 'csc'])
    @pytest.mark.parametrize('output_container', ['default', 'pandas', 'polars', None])
    @pytest.mark.parametrize('y_is_passed', (True, False))
    def test_container_accuracy_3(
        self, _X_np, _columns, _y_np, y_is_passed, input_container,
        output_container, _mock_transformer_3
    ):

        if input_container == 'np':
            _X = _X_np
        elif input_container == 'pd':
            _X = pd.DataFrame(data=_X_np, columns=_columns)
        elif input_container == 'csr':
            _X = ss.csr_array(_X_np)
        elif input_container == 'csc':
            _X = ss.csc_array(_X_np)
        else:
            raise Exception

        _og_X_dtype = type(_X)
        # transformer 3 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        trfm3 = _mock_transformer_3()
        trfm3.set_output(transform=output_container)
        trfm3.fit(_X)
        if y_is_passed:
            TRFM_X, TRFM_Y = trfm3.transform(_X, _y_np)
        else:
            TRFM_X = trfm3.transform(_X)


        if output_container is None:
            assert isinstance(TRFM_X, _og_X_dtype)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'default':
            assert isinstance(TRFM_X, np.ndarray)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'pandas':
            assert isinstance(TRFM_X, pd.DataFrame)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'polars':
            assert isinstance(TRFM_X, pl.DataFrame)
            assert TRFM_X.shape == _X.shape
        else:
            raise Exception


        # assert equality, convert TRFM_X to np

        try: TRFM_X = TRFM_X.to_array()
        except: pass

        try: TRFM_X = TRFM_X.toarray()
        except: pass

        # remember that TRFM_X was filled with fill_value from trfm3
        assert np.array_equal(TRFM_X, np.full(TRFM_X.shape, trfm3.fill_value))

        if y_is_passed:
            # y container never changes
            # always passed as np in these tests
            assert isinstance(TRFM_Y, np.ndarray)
            assert TRFM_Y.shape == _y_np.shape
            assert np.array_equal(TRFM_Y, _y_np)


        # END transformer 3 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


    @pytest.mark.parametrize('input_container', ['np', 'pd', 'csr', 'csc'])
    @pytest.mark.parametrize('output_container', ['default', 'pandas', 'polars', None])
    @pytest.mark.parametrize('y_is_passed', (True, False))
    def test_container_accuracy_4(
        self, _X_np, _columns, _y_np, y_is_passed, input_container,
        output_container, _mock_transformer_4
    ):

        if input_container == 'np':
            _X = _X_np
        elif input_container == 'pd':
            _X = pd.DataFrame(data=_X_np, columns=_columns)
        elif input_container == 'csr':
            _X = ss.csr_array(_X_np)
        elif input_container == 'csc':
            _X = ss.csc_array(_X_np)
        else:
            raise Exception

        _og_X_dtype = type(_X)

        # transformer 4 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

        trfm4 = _mock_transformer_4()
        trfm4.set_output(transform=output_container)
        if y_is_passed:
            trfm4.fit(_X)
            TRFM_X, TRFM_Y = trfm4.transform(_X, _y_np, False)
        else:
            trfm4.fit(_X)
            TRFM_X = trfm4.transform(_X, copy=False)

        if output_container is None:
            assert isinstance(TRFM_X, _og_X_dtype)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'default':
            assert isinstance(TRFM_X, np.ndarray)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'pandas':
            assert isinstance(TRFM_X, pd.DataFrame)
            assert TRFM_X.shape == _X.shape
        elif output_container == 'polars':
            assert isinstance(TRFM_X, pl.DataFrame)
            assert TRFM_X.shape == _X.shape
        else:
            raise Exception


        # assert equality, convert TRFM_X to np

        try: TRFM_X = TRFM_X.to_array()
        except: pass

        try: TRFM_X = TRFM_X.toarray()
        except: pass

        # remember that TRFM_X was filled with fill_value from trfm4
        assert np.array_equal(TRFM_X, np.full(TRFM_X.shape, trfm4.fill_value))

        if y_is_passed:
            # y container never changes
            # always passed as np in these tests
            assert isinstance(TRFM_Y, np.ndarray)
            assert TRFM_Y.shape == _y_np.shape
            assert np.array_equal(TRFM_Y, _y_np)

        # END transformer 4 ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **








