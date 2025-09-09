# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._TextLookup._shared._validation._validation \
    import _validation




class TestValidation:


    # the brunt of the work is handled by the individual validation modules,
    # which are tested separately. just make sure validation passes all good
    # and correctly handles the interdependency of parameters and the
    # specially handled words.


    @pytest.mark.parametrize('_update_lexicon', (True,))
    @pytest.mark.parametrize('_skip_numbers', (False,))
    @pytest.mark.parametrize('_auto_split', (True,))
    @pytest.mark.parametrize('_auto_add_to_lexicon', (False,))
    @pytest.mark.parametrize('_auto_delete', (True,))
    @pytest.mark.parametrize('_DELETE_ALWAYS', (list('abc'), list('mno')))
    @pytest.mark.parametrize('_REPLACE_ALWAYS',
        (dict((zip(list('abc'),list('123')))), dict((zip(list('pqr'),list('123')))))
    )
    @pytest.mark.parametrize('_SKIP_ALWAYS', (list('abc'), list('stu')))
    @pytest.mark.parametrize('_SPLIT_ALWAYS',
        (dict((zip(list('abc'), ([], [], [])))), dict((zip(list('vwx'), ([], [], [])))))
    )
    @pytest.mark.parametrize('_remove_empty_rows', (False,))
    @pytest.mark.parametrize('_verbose', (True,))
    def test_accuracy(
        self, _update_lexicon, _skip_numbers, _auto_split, _auto_add_to_lexicon,
        _auto_delete, _DELETE_ALWAYS, _REPLACE_ALWAYS, _SKIP_ALWAYS, _SPLIT_ALWAYS,
        _remove_empty_rows, _verbose
    ):

        _X = np.random.choice(list('abcde'), (5, 3), replace=True)

        _raise_for_parameter_conflict = 0
        if _auto_add_to_lexicon and not _update_lexicon:
            _raise_for_parameter_conflict += 1
        if _auto_delete and _update_lexicon:
            _raise_for_parameter_conflict += 1


        _raise_for_duplicate_in_special = False
        _equal_abc = 0
        for i in (_DELETE_ALWAYS, _REPLACE_ALWAYS, _SKIP_ALWAYS, _SPLIT_ALWAYS):
            if list(i) == list('abc'):
                _equal_abc += 1
        if _equal_abc >= 2:
            _raise_for_duplicate_in_special = True


        if _raise_for_parameter_conflict:
            with pytest.raises(ValueError):
                _validation(
                    _X,
                    _update_lexicon,
                    _skip_numbers,
                    _auto_split,
                    _auto_add_to_lexicon,
                    _auto_delete,
                    _DELETE_ALWAYS,
                    _REPLACE_ALWAYS,
                    _SKIP_ALWAYS,
                    _SPLIT_ALWAYS,
                    _remove_empty_rows,
                    _verbose
                )
        elif _raise_for_duplicate_in_special:
            with pytest.raises(ValueError):
                _validation(
                    _X,
                    _update_lexicon,
                    _skip_numbers,
                    _auto_split,
                    _auto_add_to_lexicon,
                    _auto_delete,
                    _DELETE_ALWAYS,
                    _REPLACE_ALWAYS,
                    _SKIP_ALWAYS,
                    _SPLIT_ALWAYS,
                    _remove_empty_rows,
                    _verbose
                )
        else:
            out = _validation(
                _X,
                _update_lexicon,
                _skip_numbers,
                _auto_split,
                _auto_add_to_lexicon,
                _auto_delete,
                _DELETE_ALWAYS,
                _REPLACE_ALWAYS,
                _SKIP_ALWAYS,
                _SPLIT_ALWAYS,
                _remove_empty_rows,
                _verbose
            )

            assert out is None







