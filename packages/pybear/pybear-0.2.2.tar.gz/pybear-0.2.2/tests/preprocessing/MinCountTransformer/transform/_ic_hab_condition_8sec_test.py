# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import uuid

import numpy as np

from pybear.preprocessing._MinCountTransformer._transform._ic_hab_condition \
    import _ic_hab_condition



class TestIcHabCondition:

    # def _ic_hab_condition(
    #     X: XContainer | None,
    #     _ignore_columns: IgnoreColumnsType,
    #     _handle_as_bool: HandleAsBoolType,
    #     _ignore_float_columns: bool,
    #     _ignore_non_binary_integer_columns: bool,
    #     _original_dtypes: OriginalDtypesType,
    #     _threshold: CountThresholdType,
    #     _n_features_in: int,
    #     _feature_names_in: FeatureNamesInType | None,
    #     _raise: bool = False
    # ) -> tuple[InternalIgnoreColumnsType, InternalHandleAsBoolType]:


    # fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **

    @staticmethod
    @pytest.fixture(scope='module')
    def allowed():
        return ['bin_int', 'int', 'float', 'obj']


    @staticmethod
    @pytest.fixture(scope='module')
    def _X_np(_shape):

        X = np.empty((0, _shape[0]), dtype=object)
        for c_idx in range(_shape[1]):

            if c_idx % 4 == 0:
                __ = np.random.randint(0, 2, _shape[0]).astype(np.uint8)
            elif c_idx % 4 == 1:
                __ = np.random.randint(0, 10, _shape[0]).astype(np.uint32)
            elif c_idx % 4 == 2:
                __ = np.random.uniform(0, 1, _shape[0]).astype(np.float64)
            elif c_idx % 4 == 3:
                __ = np.random.choice(list('abcde'), _shape[0], replace=True)

            X = np.vstack((X, __))

        X = X.reshape((-1, _shape[1]))

        return X


    @staticmethod
    @pytest.fixture(scope='module')
    def good_og_dtypes(_shape, allowed):

        _dtypes = np.empty(_shape[1], dtype=object)
        for c_idx in range(_shape[1]):

            _dtypes[c_idx] = allowed[c_idx % 4]

        return _dtypes

    # END fixtures ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * **


    # use Exception instead of specific errors. exceptions could be
    # raised in many submodules

    # n_features_in handled by _val_n_features_in which is tested elsewhere
    # feature_names_in handled by _val_feature_names_in which is tested elsewhere


    # X is not validated. the only places it goes to are any callables.


    # ignore_columns -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('bad_ignore_columns',
        (-2.7, -1, 0, 1, 2.7, True, 'junk', {'a':1})
    )
    def test_rejects_bad_ignore_columns(
        self, _X_np, good_og_dtypes, bad_ignore_columns, _shape
    ):

        # _ignore_columns must be None, callable, Sequence[str], Sequence[int]

        with pytest.raises(Exception):
            _ic_hab_condition(
                X=_X_np,
                _ignore_columns=bad_ignore_columns,
                _handle_as_bool=None,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=good_og_dtypes,
                _threshold=2,
                _n_features_in=_shape[1],
                _feature_names_in=None,
                _raise=False
            )


    @pytest.mark.parametrize('good_ignore_columns',
        (None, list, set, tuple, 'ndarray')
    )
    def test_accepts_good_ignore_columns(
        self, _X_np, good_og_dtypes, good_ignore_columns, _shape
    ):

        # _ignore_columns must be None, callable, Sequence[str], Sequence[int]
        # _feature_names_in: npt.NDArray[str] | None

        _base_ic = [1, _shape[1]-1]
        if good_ignore_columns is None:
            pass
        elif good_ignore_columns == 'ndarray':
            good_ignore_columns = np.array(_base_ic).astype(np.int32)
        else:
            # put in container
            good_ignore_columns = good_ignore_columns(_base_ic)

        out = _ic_hab_condition(
            X=_X_np,
            _ignore_columns=good_ignore_columns,
            _handle_as_bool=None,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=good_og_dtypes,
            _threshold=2,
            _n_features_in=_shape[1],
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        if good_ignore_columns is None:
            assert len(out[0])==0
        else:
            assert np.array_equal(out[0], _base_ic)
        assert len(out[1])==0
    # END ignore_columns -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # handle_as_bool -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('bad_handle_as_bool',
        (-2.7, -1, 0, 1, 2.7, True, 'junk', {'a':1})
    )
    def test_rejects_bad_handle_as_bool(
        self, _X_np, _shape, good_og_dtypes, bad_handle_as_bool
    ):

        # _handle_as_bool must be None, callable, Sequence[str], Sequence[int]
        # _feature_names_in: npt.NDArray[str] | None


        with pytest.raises(Exception):
            _ic_hab_condition(
                X=_X_np,
                _ignore_columns=None,
                _handle_as_bool=bad_handle_as_bool,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=good_og_dtypes,
                _threshold=2,
                _n_features_in=_shape[1],
                _feature_names_in=None,
                _raise=False
            )


    @pytest.mark.parametrize('good_handle_as_bool',
        (None, list, set, tuple, 'ndarray')
    )
    def test_accepts_good_handle_as_bool(
        self, _X_np, good_og_dtypes, good_handle_as_bool, _shape
    ):

        # only None or list-like-int
        _base_hab = [0, _shape[1]-2]
        if good_handle_as_bool is None:
            pass
        elif good_handle_as_bool == 'ndarray':
            good_handle_as_bool = np.array(_base_hab).astype(np.int32)
        else:
            # put in container
            good_handle_as_bool = good_handle_as_bool(_base_hab)

        out = _ic_hab_condition(
            X=_X_np,
            _ignore_columns=None,
            _handle_as_bool=good_handle_as_bool,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=good_og_dtypes,
            _threshold=2,
            _n_features_in=_shape[1],
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert len(out[0])==0
        if good_handle_as_bool is None:
            assert len(out[1])==0
        else:
            assert np.array_equal(out[1], _base_hab)
    # END handle_as_bool -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('handle_as_bool', (None, [], 'empty'))
    def test_hab_none_and_empty(
        self, _X_np, good_og_dtypes, handle_as_bool, _shape
    ):

        # None or empty hab short-circuits out, returns empty

        # only None or ndarray, dtype = np.int32
        if handle_as_bool == 'empty':
            handle_as_bool = np.array([]).astype(np.int32)

        out = _ic_hab_condition(
            X=_X_np,
            _ignore_columns=None,
            _handle_as_bool=handle_as_bool,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=good_og_dtypes,
            _threshold=2,
            _n_features_in=_shape[1],
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
            assert len(_)==0


    @pytest.mark.parametrize('ic', ('good', 'bad'))
    @pytest.mark.parametrize('hab', ('good', 'bad'))
    def test_catches_callable_exception(self, ic, hab):

        will_raise = False
        if ic == 'bad' or hab == 'bad':
            will_raise = True

        if ic == 'good':
            ic = lambda X: [0, 1]
        elif ic == 'bad':
            ic = lambda x: 0
        else:
            raise Exception

        if hab == 'good':
            hab = lambda X: [0, 1]
        elif hab == 'bad':
            hab = lambda X: 1
        else:
            raise Exception

        if will_raise:
            with pytest.raises(Exception):
                _ic_hab_condition(
                    X=np.random.uniform(0, 1, (5, 5)),
                    _ignore_columns=ic,
                    _handle_as_bool=hab,
                    _ignore_float_columns=False,
                    _ignore_non_binary_integer_columns=False,
                    _original_dtypes=['float' for _ in range(5)],
                    _threshold=2,
                    _n_features_in=5,
                    _feature_names_in=None,
                    _raise=False
                )
        else:
            _ic_hab_condition(
                X=np.random.uniform(0, 1, (5, 5)),
                _ignore_columns=ic,
                _handle_as_bool=hab,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=['float' for _ in range(5)],
                _threshold=2,
                _n_features_in=5,
                _feature_names_in=None,
                _raise=False
            )


    # threshold -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('bad_threshold',
        (-2.7, -1, 0, 1, 2.7, True, 'junk', {'a':1}, lambda x: x)
    )
    def test_rejects_bad_threshold(
        self, _X_np, _shape, good_og_dtypes, bad_threshold
    ):

        # only int or list-like-int

        with pytest.raises(Exception):
            _ic_hab_condition(
                X=_X_np,
                _ignore_columns=None,
                _handle_as_bool=None,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=good_og_dtypes,
                _threshold=bad_threshold,
                _n_features_in=_shape[1],
                _feature_names_in=None,
                _raise=False
            )


    @pytest.mark.parametrize('good_threshold', ('int', 'Sequence[int]'))
    def test_accepts_good_threshold(
        self, _X_np, good_og_dtypes, good_threshold, _shape
    ):

        if good_threshold == 'int':
            _threshold = 2
        elif good_threshold == 'Sequence[int]':
            _threshold = [2 for _ in range(_shape[1])]
        else:
            raise Exception

        out = _ic_hab_condition(
            X=_X_np,
            _ignore_columns=None,
            _handle_as_bool=None,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=good_og_dtypes,
            _threshold=_threshold,
            _n_features_in=_shape[1],
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
            assert len(_)==0
    # END threshold -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('og_dtypes', ['short', 'good', 'long'])
    @pytest.mark.parametrize('ignore_columns', ['low', 'good', 'high'])
    @pytest.mark.parametrize('handle_as_bool', ['low', 'good', 'high'])
    @pytest.mark.parametrize('threshold', ['short', 'good', 'long'])
    def test_rejects_bad_param_lens_wrt_n_features_in(
        self, _X_np, allowed, og_dtypes, ignore_columns, handle_as_bool,
        threshold, _shape
    ):

        len_dict = {
            'short': _shape[1] // 2,
            'good': _shape[1],
            'long': 2 * _shape[1]
        }

        idx_dict = {
            'low': [-_shape[1]-1, 0, 1],
            'good': [0, 1, _shape[1]-1],
            'high': [0, 1, _shape[1]]
        }

        _og_dtypes = np.random.choice(allowed, len_dict[og_dtypes], replace=True)
        _ignore_columns = np.array(idx_dict[ignore_columns]).astype(np.int32)
        _handle_as_bool = np.array(idx_dict[handle_as_bool]).astype(np.int32)
        _threshold = [2 for _ in range(len_dict[threshold])]

        if og_dtypes=='good' and ignore_columns=='good' \
                and handle_as_bool=='good' and threshold=='good':

            _ic_hab_condition(
                X=_X_np,
                _ignore_columns=_ignore_columns,
                _handle_as_bool=_handle_as_bool,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=_og_dtypes,
                _threshold=_threshold,
                _n_features_in=_shape[1],
                _feature_names_in=None,
                _raise=False
            )

        else:
            with pytest.raises(Exception):
                _ic_hab_condition(
                    X=_X_np,
                    _ignore_columns=_ignore_columns,
                    _handle_as_bool=_handle_as_bool,
                    _ignore_float_columns=False,
                    _ignore_non_binary_integer_columns=False,
                    _original_dtypes=_og_dtypes,
                    _threshold=_threshold,
                    _n_features_in=_shape[1],
                    _feature_names_in=None,
                    _raise=False
                )


    # raise -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_raise',
        (-2.7, -1, 0, 1, 2.7, None, 'junk', [0,1], {'a':1}, lambda x: x)
    )
    def test_rejects_junk_raise(self, _X_np, junk_raise):

        with pytest.raises(TypeError):
            _ic_hab_condition(
                X=_X_np,
                _ignore_columns=[1, 3],
                _handle_as_bool=[0, 2],
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=['obj', 'float', 'obj', 'bin_int'],
                _threshold=2,
                _n_features_in=4,
                _feature_names_in=None,
                _raise=junk_raise
            )


    @pytest.mark.parametrize('bool_raise', (True, False))
    def test_accepts_bool_raise(
        self, _X_np, _shape, good_og_dtypes, bool_raise
    ):

        _ic_hab_condition(
            X=_X_np,
            _ignore_columns=None,
            _handle_as_bool=None,
            _ignore_float_columns=True,
            _ignore_non_binary_integer_columns=True,
            _original_dtypes=good_og_dtypes,
            _threshold=2,
            _n_features_in=_shape[1],
            _feature_names_in=[str(uuid.uuid4)[:5] for _ in range(_shape[1])],
            _raise=bool_raise
        )
    # END raise -- -- -- -- -- -- -- -- -- --


    # v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^

    @pytest.mark.parametrize('good_ic',
        (
            None, lambda X: [0, 2], lambda X: ['a', 'b'], [], [1, 0], (0, 2),
            np.array([1, 2])
        )
    )
    @pytest.mark.parametrize('good_hab',
        (
            None, lambda X: [0, 2], lambda X: ['a', 'b'], [], [1, 0], (0, 2),
            np.array([1, 2])
        )
    )
    @pytest.mark.parametrize('fni', (True, False))
    def test_convert_accuracy(self, good_ic, good_hab, fni):


        _shape = (10, 3)

        X = np.random.uniform(0, 1, _shape)

        if fni:
            fni = list('abcdefghijklmnopqrstv')[:_shape[1]]
        elif not fni:
            fni = None

        # cant have str ic/hab when fni is None
        will_fail = False
        if fni is None:
            # ic callable returns vector of str
            if callable(good_ic):
                if isinstance(good_ic(X)[0], str):
                    will_fail = True
            elif good_ic is None:
                pass
            elif len(good_ic) == 0:
                pass
            # ic passed as vector of str
            elif all(map(isinstance, good_ic, (str for _ in good_ic))):
                will_fail = True

            # hab callable returns vector of str
            if callable(good_hab):
                if isinstance(good_hab(X)[0], str):
                    will_fail = True
            elif good_hab is None:
                pass
            elif len(good_hab) == 0:
                pass
            # hab passed as vector str
            elif all(map(isinstance, good_hab, (str for _ in good_hab))):
                will_fail = True

        if will_fail:
            with pytest.raises(Exception):
                _ic_hab_condition(
                    X=X,
                    _ignore_columns=good_ic,
                    _handle_as_bool=good_hab,
                    _ignore_float_columns=False,
                    _ignore_non_binary_integer_columns=False,
                    _original_dtypes=['float' for _ in range(3)],
                    _threshold=2,
                    _n_features_in=3,
                    _feature_names_in=fni,
                    _raise=False
                )
            pytest.skip(reason=f"cant do anymore tests after except")
        else:

            out = _ic_hab_condition(
                X=X,
                _ignore_columns=good_ic,
                _handle_as_bool=good_hab,
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=['float' for _ in range(3)],
                _threshold=2,
                _n_features_in=3,
                _feature_names_in=fni,
                _raise=False
            )


            if good_ic is None:
                assert np.array_equal(out[0], [])
                assert out[0].dtype == np.int32
            elif callable(good_ic) and isinstance(good_ic(X)[0], str):
                if fni is None:
                    # should have failed & skipped above
                    raise Exception
                else:
                    assert np.array_equal(out[0], [0, 1])
                    assert out[0].dtype == np.int32
            elif np.array_equal(good_ic, [0, 2]):
                assert np.array_equal(out[0], [0, 2])
                assert out[0].dtype == np.int32
            elif callable(good_ic) and isinstance(good_ic(X)[0], int):
                assert np.array_equal(out[0], [0, 2])
                assert out[0].dtype == np.int32
            elif np.array_equal(good_ic, ['a', 'b']):
                if fni is None:
                    # should have failed & skipped above
                    raise Exception
                else:
                    assert np.array_equal(out[0], [0, 1])
                    assert out[0].dtype == np.int32
            elif len(good_ic) == 0:
                assert len(out[0]) == 0
                assert isinstance(out[0], np.ndarray)
                assert out[0].dtype == np.int32
            elif np.array_equal(good_ic, [1, 0]):
                assert np.array_equal(out[0], [1, 0])
                assert out[0].dtype == np.int32
            elif np.array_equal(good_ic, (0, 2)):
                assert np.array_equal(out[0], [0, 2])
                assert out[0].dtype == np.int32
            elif np.array_equal(good_ic, np.array([1, 2])):
                assert np.array_equal(out[0], [1, 2])
                assert out[0].dtype == np.int32
            else:
                raise Exception


            if good_hab is None:
                assert np.array_equal(out[1], [])
                assert out[1].dtype == np.int32
            elif callable(good_hab) and isinstance(good_hab(X)[0], str):
                if fni is None:
                    # should have failed & skipped above
                    raise Exception
                else:
                    assert np.array_equal(out[1], [0, 1])
                    assert out[1].dtype == np.int32
            elif np.array_equal(good_hab, [0, 2]):
                assert np.array_equal(out[1], [0, 2])
                assert out[1].dtype == np.int32
            elif callable(good_hab) and isinstance(good_hab(X)[0], int):
                assert np.array_equal(out[1], [0, 2])
                assert out[1].dtype == np.int32
            elif np.array_equal(good_hab, ['a', 'b']):
                if fni is None:
                    # should have failed & skipped above
                    raise Exception
                else:
                    assert np.array_equal(out[1], [0, 1])
                    assert out[1].dtype == np.int32
            elif len(good_hab) == 0:
                assert len(out[1]) == 0
                assert isinstance(out[1], np.ndarray)
                assert out[1].dtype == np.int32
            elif np.array_equal(good_hab, [1, 0]):
                assert np.array_equal(out[1], [1, 0])
                assert out[1].dtype == np.int32
            elif np.array_equal(good_hab, (0, 2)):
                assert np.array_equal(out[1], [0, 2])
                assert out[1].dtype == np.int32
            elif np.array_equal(good_hab, np.array([1, 2])):
                assert np.array_equal(out[1], [1, 2])
                assert out[1].dtype == np.int32
            else:
                raise Exception


    options = ('none', 'empty', 'vector1', 'vector2', 'vector3')
    @pytest.mark.parametrize('_handle_as_bool', options)
    @pytest.mark.parametrize('_ignore_columns', options)
    @pytest.mark.parametrize('_ignore_float_columns', (True, False))
    @pytest.mark.parametrize('_ignore_non_binary_integer_columns', (True, False))
    @pytest.mark.parametrize('_threshold', ('int', 'Sequence[int]'))
    def test_ignore_conflict_warn_accuracy(
        self, _X_np, good_og_dtypes, _shape, _handle_as_bool,
        _threshold, _ignore_columns, _ignore_float_columns,
        _ignore_non_binary_integer_columns
    ):

        if _shape[1] < 6:
            raise Exception(f"'n_features_in' must be >= 6 for this test")

        # if intersection between ignore_float_columns and ignore_columns,
        # doesnt matter, ignored either way

        # if intersection between ignore_non_binary_integer_columns and
        # ignore_columns, doesnt matter, ignored either way

        # so we need to address when
        # warn on handle_as_bool intersects ignore_columns
        # warn on handle_as_bool intersects ignore_float_columns
        # warn on handle_as_bool intersects ignore_non_binary_integer_columns
        # warn on handle_as_bool intersects threshold==1


        vector1 = [0, 1, 2]
        vector2 = [_shape[1]-3, _shape[1]-2, _shape[1]-1]
        vector3 = [-2, -3, -4]

        param_input_dict = {
            'none': None,
            'empty': np.array([], dtype=np.int32).ravel(),
            'vector1': np.array(vector1, dtype=np.int32).ravel(),
            'vector2': np.array(vector2, dtype=np.int32).ravel(),
            'vector3': np.array(vector3, dtype=np.int32).ravel()
        }

        hab = param_input_dict[_handle_as_bool]
        ic = param_input_dict[_ignore_columns]

        if _ignore_float_columns:
            _float_columns = np.arange(_shape[1])[(good_og_dtypes=='float')]
        else:
            _float_columns = np.array([])

        if _ignore_non_binary_integer_columns:
            _non_bin_int_columns = np.arange(_shape[1])[(good_og_dtypes=='int')]
        else:
            _non_bin_int_columns = np.array([])

        if _threshold == 'int':
            _threshold = 2
        else:
            while True:
                _threshold = \
                    [int(np.random.randint(1, 3)) for _ in range(_shape[1])]
                if 1 in _threshold and 2 in _threshold:
                    break

        if hab is not None:
            if ic is not None:
                hab_vs_ic = \
                    bool(len(set(list(hab)).intersection(list(ic))))
            else:
                hab_vs_ic = False
            hab_vs_ign_flt = \
                bool(len(set(list(hab)).intersection(list(_float_columns))))
            hab_vs_ign_non_bin_int = \
                bool(len(set(list(hab)).intersection(list(_non_bin_int_columns))))
            if isinstance(_threshold, int):
                hab_vs_threshold = False
            else:
                __ = np.array(_threshold)
                __ = np.arange(len(__))[(__==1)]
                hab_vs_threshold = bool(len(set(list(hab)).intersection(__)))
        else:
            hab_vs_ic = False
            hab_vs_ign_flt = False
            hab_vs_ign_non_bin_int = False
            hab_vs_threshold = False


        del _float_columns, _non_bin_int_columns

        # warn on handle_as_bool intersects ignore_columns
        # warn on handle_as_bool intersects ignore_float_columns
        # warn on handle_as_bool intersects ignore_non_binary_integer_columns
        # warn on handle_as_bool intersects threshold==1

        # handle_as_bool is None or empty, never warn.
        if hab_vs_ic or hab_vs_ign_flt or hab_vs_ign_non_bin_int \
                or hab_vs_threshold:
            with pytest.warns():
                out = _ic_hab_condition(
                    X=_X_np,
                    _ignore_columns=ic,
                    _handle_as_bool=hab,
                    _ignore_float_columns=_ignore_float_columns,
                    _ignore_non_binary_integer_columns= \
                        _ignore_non_binary_integer_columns,
                    _original_dtypes=good_og_dtypes,
                    _threshold=_threshold,
                    _n_features_in=_shape[1],
                    _feature_names_in=None,
                    _raise=False
                )

        else:
            out = _ic_hab_condition(
                X=_X_np,
                _ignore_columns=ic,
                _handle_as_bool=hab,
                _ignore_float_columns=_ignore_float_columns,
                _ignore_non_binary_integer_columns= \
                    _ignore_non_binary_integer_columns,
                _original_dtypes=good_og_dtypes,
                _threshold=_threshold,
                _n_features_in=_shape[1],
                _feature_names_in=None,
                _raise=False
            )

        assert isinstance(out, tuple)

        assert isinstance(out[0], (list, np.ndarray))

        if _ignore_columns in ['none', 'empty']:
            assert len(out[0])==0
        elif _ignore_columns == 'vector1':
            assert np.array_equal(out[0], vector1)
        elif _ignore_columns == 'vector2':
            assert np.array_equal(
                out[0],
                [_shape[1]-3, _shape[1]-2, _shape[1]-1]
            )
        elif _ignore_columns == 'vector3':
            assert np.array_equal(
                out[0],
                [_shape[1]-2, _shape[1]-3, _shape[1]-4]
            )
        else:
            raise Exception

        assert isinstance(out[1], (list, np.ndarray))

        if _handle_as_bool in ['none', 'empty']:
            assert len(out[1])==0
        elif _handle_as_bool == 'vector1':
            assert np.array_equal(out[1], vector1)
        elif _handle_as_bool == 'vector2':
            assert np.array_equal(
                out[1],
                [_shape[1]-3, _shape[1]-2, _shape[1]-1]
            )
        elif _handle_as_bool == 'vector3':
            assert np.array_equal(
                out[1],
                [_shape[1]-2, _shape[1]-3, _shape[1]-4]
            )
        else:
            raise Exception


    def test_warns_excepts_hab_on_obj(self, _X_np):

        _X = np.vstack((
            _X_np[:, 1],
            _X_np[:, 1],
            _X_np[:, 3],
            _X_np[:, 3],
            _X_np[:, 3]
        )).reshape((-1, 5))

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        with pytest.raises(ValueError):
            _ic_hab_condition(
                X=_X,
                _ignore_columns=[],
                _handle_as_bool=[-2, -1],
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=['int', 'int'] + ['obj' for _ in range(3)],
                _threshold=2,
                _n_features_in=5,
                _feature_names_in=None,
                _raise=True
            )

        with pytest.warns():
            _ic_hab_condition(
                X=_X,
                _ignore_columns=[],
                _handle_as_bool=[-2, -1],
                _ignore_float_columns=False,
                _ignore_non_binary_integer_columns=False,
                _original_dtypes=['int', 'int'] + ['obj' for _ in range(3)],
                _threshold=2,
                _n_features_in=5,
                _feature_names_in=None,
                _raise=False
            )

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def test_accepts_ignored_hab_on_obj(self, _X_np):
        out = _ic_hab_condition(
            X=np.vstack((
                _X_np[:, 1],
                _X_np[:, 1],
                _X_np[:, 1],
                _X_np[:, 3]
            )).reshape((-1, 4)),
            _ignore_columns=[-4, -2, -1],
            _handle_as_bool=[-3, -1],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=tuple(['int', 'int', 'int', 'obj']),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert np.array_equal(out[0], [4 - 4, 4 - 2, 4 - 1])
        assert np.array_equal(out[1], [4 - 3, 4 - 1])


    def test_accept_hab_on_numeric(self, _X_np):

        out = _ic_hab_condition(
            X=np.vstack((
                _X_np[:, 1],
                _X_np[:, 2],
                _X_np[:, 0],
                _X_np[:, 3]
            )).reshape((-1, 4)),
            _ignore_columns=None,
            _handle_as_bool=[0, 1, 2],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=set(('int', 'float', 'bin_int', 'obj')),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert len(out[0])==0
        assert np.array_equal(out[1], [0, 1, 2])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = _ic_hab_condition(
            X=np.vstack((
                _X_np[:, 1],
                _X_np[:, 2],
                _X_np[:, 0],
                _X_np[:, 3]
            )).reshape((-1, 4)),
            _ignore_columns=None,
            _handle_as_bool=[-4, -3, -2],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=np.array(['int', 'float', 'bin_int', 'obj']),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=None,
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert len(out[0])==0
        assert np.array_equal(out[1], [4 - 4, 4 - 3, 4 - 2])


    # this is for print_instructions. prove out that when ic/hab are
    # given as Sequence[int], Sequence[str], or None, X doesnt matter,
    # Sequence[str] is converted to Sequence[int], Sequence[int] is
    # mapped to positive, and None is converted to empty.
    def test_print_instructions_conditions(self, _X_np):


        # Sequence[str]
        out = _ic_hab_condition(
            X=None,
            _ignore_columns=['c', 'a'],
            _handle_as_bool=['b', 'd'],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=tuple(['int', 'int', 'obj', 'int']),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=list('abcd'),
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert np.array_equal(out[0], [2, 0])
        assert np.array_equal(out[1], [1, 3])

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # Sequence[int]
        out = _ic_hab_condition(
            X=None,
            _ignore_columns=[-3, -2],
            _handle_as_bool=[-1, -4],
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=tuple(['int', 'int', 'obj', 'int']),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=list('abcd'),
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert np.array_equal(out[0], [1, 2])
        assert np.array_equal(out[1], [3, 0])


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # None
        out = _ic_hab_condition(
            X=None,
            _ignore_columns=None,
            _handle_as_bool=None,
            _ignore_float_columns=False,
            _ignore_non_binary_integer_columns=False,
            _original_dtypes=tuple(['int', 'int', 'obj', 'int']),
            _threshold=2,
            _n_features_in=4,
            _feature_names_in=list('abcd'),
            _raise=False
        )

        assert isinstance(out, tuple)
        for _ in out:
            iter(_)
        assert len(out[0])==0
        assert len(out[1])==0


        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --



