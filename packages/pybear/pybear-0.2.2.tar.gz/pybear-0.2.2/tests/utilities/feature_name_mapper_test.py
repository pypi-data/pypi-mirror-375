# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.utilities._feature_name_mapper import feature_name_mapper

import numpy as np
import pandas as pd

import pytest



class TestColumnNameMapper:


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # feature_names -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_fn',
        (-2.7, -1, 0, 1, 2.7, True, 'junk', {'a':1}, lambda x: x)
    )
    def test_feature_names_rejects_junk(self, junk_fn):
        with pytest.raises(TypeError):
            feature_name_mapper(
                junk_fn,
                set('abcde'),
                positive=True
            )


    @pytest.mark.parametrize('bad_fn',
        ('list_bool', 'np', 'pd')
    )
    def test_feature_names_rejects_bad(self, bad_fn):

        if bad_fn == 'list_bool':
            bad_fn = [True, False]
        elif bad_fn == 'np':
            bad_fn = np.random.randint(0, 10, (3, 3))
        elif bad_fn == 'pd':
            bad_fn = pd.DataFrame(
                data=np.random.randint(0, 10, (3, 3)),
                columns=['A', 'B', 'C']
            )
        else:
            raise Exception

        with pytest.raises(TypeError):
            feature_name_mapper(
                bad_fn,
                tuple('abcde'),
                positive=True
            )


    @pytest.mark.parametrize('good_fn',
        (
            list('abcd'),
            tuple('abcd'),
            set('abcd'),
            np.array(list('abcd')),
            [1,2,3],
            set((-1, -2, -3)),
            (0, 1, 2),
             np.array([12, 13, 14])
        )
    )
    def test_feature_names_accepts_good(self, good_fn):

        out = feature_name_mapper(
            good_fn,
            np.array(list('abcdefghijklmnop')),
            positive=None
        )

        assert isinstance(out, np.ndarray)
    # feature_names -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # feature_names_in -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_fni',
        (-2.7, -1, 0, 1, 2.7, True, 'junk', {'a':1}, lambda x: x)
    )
    def test_feature_names_in_rejects_junk(self, junk_fni):
        with pytest.raises(TypeError):
            feature_name_mapper(
                None,
                junk_fni,
                positive=True
            )

    @pytest.mark.parametrize('bad_fni',
        ('list_int', 'list_bool', 'np', 'pd', 'double_list_str', 'empty')
    )
    def test_feature_names_in_rejects_bad(self, bad_fni):

        if bad_fni == 'list_int':
            bad_fni = [1, 2, 3]
        elif bad_fni == 'list_bool':
            bad_fni = [True, False]
        elif bad_fni == 'np':
            bad_fni = np.random.randint(0,10, (3,3))
        elif bad_fni == 'pd':
            bad_fni = pd.DataFrame(
                data=np.random.randint(0,10, (3,3)),
                columns=list('abc')
            )
        elif bad_fni == 'double_list_str':
            bad_fni = [list('abc')]
        elif bad_fni == 'empty':
            bad_fni = []
        else:
            raise Exception

        with pytest.raises(TypeError):
            feature_name_mapper(
                None,
                bad_fni,
                positive=True
            )

    @pytest.mark.parametrize('good_fni',
        (
            list('abcd'),
            tuple('abcd'),
            set('abcd'),
            np.array(list('abcd'))
        )
    )
    def test_feature_names_in_accepts_1D_of_strings(self, good_fni):

        out = feature_name_mapper(
            None,
            good_fni,
            positive=True
        )

        assert out is None
    # END feature_names_in -- -- -- -- -- -- -- -- -- -- -- -- --

    # positive -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_positive',
        (-2.7, -1, 0, 1, 2.7, 'junk', [0,1], (1,), {'a':1}, lambda x: x)
    )
    def test_positive_rejects_junk(self, junk_positive):
        with pytest.raises(TypeError):
            feature_name_mapper(
                None,
                list('abcd'),
                junk_positive
            )


    @pytest.mark.parametrize('good_positive', (True, False, None))
    def test_positive_accepts_bool_or_none(self, good_positive):

        out = feature_name_mapper(
            None,
            list('abcdef'),
            positive=good_positive
        )

        assert out is None
    # END positive -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # joint -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('bad_fn_indices',
        ([-100, -99, -98], [98, 99, 100])
    )
    def test_fn_indices_out_of_range(self, bad_fn_indices):

        with pytest.raises(ValueError):
            feature_name_mapper(
                bad_fn_indices,
                tuple('abcde'),
                positive=None
            )


    def test_feature_names_as_str_no_fni(self):

        with pytest.raises(ValueError):
            feature_name_mapper(
                list('abc'),
                None,
                positive=None
            )
    # END joint -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # accuracy -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('feature_names',
        (
            [-2, -1], [1, 3], np.array([0, -1], dtype=np.int32),
            np.array(['c', 'd'], dtype='<U1'), ('d', 'b'), {'a', 'd'},
            list('aaabbb'), list('ccbb')
        )
    )
    @pytest.mark.parametrize('feature_names_in',
        (list('abcdefg'), np.array(list('abcdefg'), dtype='<U1'))
    )
    @pytest.mark.parametrize('positive', (True, False, None))
    def test_accuracy(
        self, feature_names, feature_names_in, positive
    ):

        # also test that 'feature_names' and 'feature_names_in' are not mutated

        # pytest appears to have erratic behavior when injecting a set.
        # sometimes the {'a', 'd'} set is being passed to feature_name_mapper
        # as {'d', 'a'}. when this happens, skip the test:
        if list(feature_names) == ['d', 'a']:
            pytest.skip(reason=f"pytest changed the input")

        if positive not in [True, False, None]:
            raise Exception

        # -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # get pre-function states of 'feature_names' and 'feature_names_in'
        _og_fn_type = type(feature_names)
        if isinstance(feature_names, np.ndarray):
            _og_fn_dtype = feature_names.dtype

        _og_fni_type = type(feature_names_in)
        if isinstance(feature_names_in, np.ndarray):
            _og_fni_dtype = feature_names_in.dtype
        # -- -- -- -- -- -- -- -- -- -- -- -- -- --

        out = feature_name_mapper(
            feature_names,
            feature_names_in,
            positive=positive
        )

        assert isinstance(out, np.ndarray)
        assert out.dtype == np.int32

        # check 'feature_names' and 'feature_names_in' are not mutated - - - -
        assert type(feature_names) is _og_fn_type
        if isinstance(feature_names, np.ndarray):
            assert feature_names.dtype == _og_fn_dtype
            del _og_fn_dtype
        del _og_fn_type

        assert type(feature_names_in) is _og_fni_type
        if isinstance(feature_names_in, np.ndarray):
            assert _og_fni_dtype == feature_names_in.dtype
            del _og_fni_dtype
        del _og_fni_type
        # EMD check 'feature_names' and 'feature_names_in' are not mutated - -

        max_dim = len(feature_names_in)

        if np.array_equal(feature_names, [-2, -1]):
            if positive is True:
                assert np.array_equiv(out, [max_dim - 2, max_dim - 1])
            elif positive is False:
                assert np.array_equiv(out, [-2, -1])
            elif positive is None:
                assert np.array_equiv(out, [-2, -1])
        elif np.array_equal(feature_names, [1, 3]):
            if positive is True:
                assert np.array_equiv(out, [1, 3])
            elif positive is False:
                assert np.array_equiv(out, [1 - max_dim, 3 - max_dim])
            elif positive is None:
                assert np.array_equiv(out, [1, 3])
        elif np.array_equal(feature_names, [0, -1]):
            if positive is True:
                assert np.array_equiv(out, [0, max_dim-1])
            elif positive is False:
                assert np.array_equiv(out, [-max_dim, -1])
            elif positive is None:
                assert np.array_equiv(out, [0, -1])
        elif np.array_equal(feature_names, ['c', 'd']):
            if positive is True:
                assert np.array_equiv(out, [2, 3])
            elif positive is False:
                assert np.array_equiv(out, [-max_dim+2, -max_dim+3])
            elif positive is None:
                assert np.array_equiv(out, [2, 3])
        elif feature_names == ('d', 'b'):
            if positive is True:
                assert np.array_equiv(out, [3, 1])
            elif positive is False:
                assert np.array_equiv(out, [-max_dim+3, -max_dim+1])
            elif positive is None:
                assert np.array_equiv(out, [3, 1])
        elif feature_names == {'a', 'd'}:
            # set sorts them
            if positive is True:
                assert np.array_equiv(out, [0, 3])
            elif positive is False:
                assert np.array_equiv(out, [-max_dim, -max_dim+3])
            elif positive is None:
                assert np.array_equiv(out, [0, 3])
        elif feature_names == list('aaabbb'):
            if positive is True:
                assert np.array_equiv(out, [0, 0, 0, 1, 1, 1])
            elif positive is False:
                assert np.array_equiv(
                    out,
                    [-max_dim, -max_dim, -max_dim, -max_dim+1, -max_dim+1, -max_dim+1],
                )
            elif positive is None:
                assert np.array_equiv(out, [0, 0, 0, 1, 1, 1])
        elif feature_names == list('ccbb'):
            if positive is True:
                assert np.array_equiv(out, [2, 2, 1, 1])
            elif positive is False:
                assert np.array_equiv(
                    out,
                    [-max_dim+2, -max_dim+2, -max_dim+1, -max_dim+1]
                )
            elif positive is None:
                assert np.array_equiv(out, [2, 2, 1, 1])
        else:
            raise Exception






