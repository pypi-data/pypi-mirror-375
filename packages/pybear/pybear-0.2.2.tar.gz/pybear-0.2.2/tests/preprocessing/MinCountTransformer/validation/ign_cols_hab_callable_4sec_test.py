# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer._validation.\
    _ign_cols_hab_callable import _val_ign_cols_hab_callable



class TestValIgnColsHabCallable:


    # _n_features_in is validated by _val_n_features_in, tested elsewhere

    # _feature_names_in is validated by _val_feature_names_in, tested elsewhere

    # validate _name -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_name',
        (-2.7, -1, 0, 1, 2.7, True, None, [0, 1], (1,), {'a':1}, lambda x: x)
    )
    def test_rejects_junk_name(self, junk_name):
        with pytest.raises(TypeError):
            _val_ign_cols_hab_callable(
                [0, 1],
                None,
                junk_name,
                10,
                None
            )


    @pytest.mark.parametrize('bad_name', ('wings', 'chips', 'beer'))
    def test_rejects_bad_name(self, bad_name):
        with pytest.raises(ValueError):
            _val_ign_cols_hab_callable(
                [0, 1],
                None,
                bad_name,
                10,
                None
            )


    @pytest.mark.parametrize('good_name', ('ignore_columns', 'handle_as_bool'))
    def test_accepts_good_name(self, good_name):
        _val_ign_cols_hab_callable(
            [0, 1],
            None,
            good_name,
            10,
            None
        )
    # END validate _name -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    # validate _fxn_output -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_fxn_output',
        (-2.7, -1, 0, 1, 2.7, True, False, None, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_fxn_output(self, junk_fxn_output):
        with pytest.raises(TypeError):
            _val_ign_cols_hab_callable(
                junk_fxn_output,
                None,
                'ignore_columns',
                13,
                np.array(list('abcdefghijklm'))
            )


    @pytest.mark.parametrize('bad_fxn_output',
        ((True, False), [[1,2,3], [4,5,6]], ['a', 1, 'b', 2])
    )
    def test_rejects_bad_fxn_output(self, bad_fxn_output):
        with pytest.raises(TypeError):
            _val_ign_cols_hab_callable(
                bad_fxn_output,
                None,
                'handle_as_bool',
                13,
                np.array(list('abcdefghijklm'))
            )


    @pytest.mark.parametrize('good_fxn_output',
        ([1, 2, 3], np.array(list('abc')), {0, 2, 3}, ('d', 'e', 'f'))
    )
    def test_accepts_good_fxn_output(self, good_fxn_output):

        # 1D list-like, all int or all str

        out = _val_ign_cols_hab_callable(
            good_fxn_output,
            None,
            'ignore_columns',
            13,
            np.array(list('abcdefghijklm'))
        )

        assert out is None

    # END validate _fxn_output -- -- -- -- -- -- -- -- -- -- -- -- -- --


    # validate _first_fxn_output -- -- -- -- -- -- -- -- -- -- -- -- --
    @pytest.mark.parametrize('junk_first_fxn_output',
        (-2.7, -1, 0, 1, 2.7, True, False, {'a':1}, lambda x: x)
    )
    def test_rejects_junk_first_fxn_output(self, junk_first_fxn_output):
        with pytest.raises(ValueError):
            # this fails for != _fxn_output
            _val_ign_cols_hab_callable(
                [0, 1, 2],
                junk_first_fxn_output,
                'ignore_columns',
                13,
                np.array(list('abcdefghijklm'))
            )


    @pytest.mark.parametrize('bad_first_fxn_output',
        ((True, False), [[1,2,3], [4,5,6]], ['a', 1, 'b', 2])
    )
    def test_rejects_bad_first_fxn_output(self, bad_first_fxn_output):
        with pytest.raises(ValueError):
            # this fails for != _fxn_output
            _val_ign_cols_hab_callable(
                [2,3,4],
                bad_first_fxn_output,
                'handle_as_bool',
                13,
                np.array(list('abcdefghijklm'))
            )


    @pytest.mark.parametrize('good_first_fxn_output',
        ([1, 2, 3], np.array(list('abc')), {0, 2, 3}, ('d', 'e', 'f'))
    )
    def test_accepts_good_first_fxn_output(self, good_first_fxn_output):

        # 1D list-like, all int or all str
        out = _val_ign_cols_hab_callable(
            good_first_fxn_output,
            good_first_fxn_output,  # must match current output to pass
            'ignore_columns',
            13,
            np.array(list('abcdefghijklm'))
        )

        assert out is None

    # END validate _first_fxn_output -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


    @pytest.mark.parametrize('empty_fxn_output', ([], np.array([])))
    def test_passes_empty(self, empty_fxn_output):
        out = _val_ign_cols_hab_callable(
            empty_fxn_output,
            None,
            'handle_as_bool',
            12,
            None
        )

        assert out is None


    def test_rejects_str_output_no_fni(self):
        with pytest.raises(ValueError):
            _val_ign_cols_hab_callable(
                list('abc'),
                None,
                'handle_as_bool',
                12,
                None
            )


    @pytest.mark.parametrize('bad_fn', ('x', 'y', 'z'))
    def test_rejects_str_output_not_in_fni(self, bad_fn):
        with pytest.raises(TypeError):
            _val_ign_cols_hab_callable(
                bad_fn,
                None,
                'ignore_columns',
                6,
                np.array(list('abcdef'))
            )


    @pytest.mark.parametrize('bad_idxs',
        ([99, 100, 101], (-38, -33, -27), {-19, 25})
    )
    def test_rejects_index_out_of_range(self, bad_idxs):
        with pytest.raises(ValueError):
            _val_ign_cols_hab_callable(
                bad_idxs,
                None,
                'handle_as_bool',
                6,
                np.array(list('abcdef'))
            )


    @pytest.mark.parametrize('_fxn_output', (list('abc'), [-2, -1, 0], ['c', 'd']))
    @pytest.mark.parametrize('_name', ('ignore_columns', 'handle_as_bool'))
    @pytest.mark.parametrize('_feature_names_in', (None, np.array(list('abcdefgh'))))
    def test_accepts_good(self, _fxn_output, _name, _feature_names_in):

        # the only thing that should fail is passing str output w/o
        # feature_names_in
        # index output works with or without feature_names_in

        if all(map(isinstance, _fxn_output, (str for _ in _fxn_output))) \
                and _feature_names_in is None:
            with pytest.raises(ValueError):
                _val_ign_cols_hab_callable(
                    _fxn_output,
                    None,
                    _name,
                    8,
                    _feature_names_in
                )
        else:
            out = _val_ign_cols_hab_callable(
                _fxn_output,
                None,
                _name,
                8,
                _feature_names_in
            )

            assert out is None



    @pytest.mark.parametrize('_fxn_output', (list('abc'), [-2, -1, 0], ['c', 'd']))
    @pytest.mark.parametrize('_first_fxn_output',
        (list('abc'), [-2, -1, 0], ['c', 'd'])
    )
    @pytest.mark.parametrize('_name', ('ignore_columns', 'handle_as_bool'))
    def test_rejects_current_does_not_equal_first(
        self, _fxn_output, _first_fxn_output, _name
    ):

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _n_features_in = 8

        # if _fxn_output is strs, must pass feature_names_in
        if all(map(isinstance, _fxn_output, (str for _ in _fxn_output))):
            _feature_names_in = list('abcdefghijklmopqurstuv')[:_n_features_in]
        else:
            _feature_names_in = None
        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _first_fxn_output is not None \
                and not np.array_equal(_fxn_output, _first_fxn_output):
            with pytest.raises(ValueError):
                _val_ign_cols_hab_callable(
                    _fxn_output,
                    _first_fxn_output,
                    _name,
                    _n_features_in=_n_features_in,
                    _feature_names_in=_feature_names_in
                )
        else:
            out = _val_ign_cols_hab_callable(
                _fxn_output,
                _first_fxn_output,
                _name,
                _n_features_in=_n_features_in,
                _feature_names_in=_feature_names_in
            )

            assert out is None




