# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._AutoTextCleaner._validation._validation \
    import _validation

import re

import pytest



class TestValidation:


    # most of the heavy lifting is handled by the submodules, which have
    # their own tests. just make sure this works and passes all good.


    @staticmethod
    @pytest.fixture(scope='module')
    def _X1():
        return list('abcdefghijklmnop')


    @staticmethod
    @pytest.fixture(scope='module')
    def _X2():
        return [
            list('abcdefghij'),
            list('abcdefghijklmnop'),
            list('abcdefg'),
            list('abcdefghijkl')
        ]


    @pytest.mark.parametrize('_X_dim', (1, 2))
    @pytest.mark.parametrize('global_sep', (' ', ','))
    @pytest.mark.parametrize('case_sensitive', (True, )) # False))
    @pytest.mark.parametrize('global_flags', (None, re.I))
    @pytest.mark.parametrize('remove_empty_rows', (True, )) #False))
    @pytest.mark.parametrize('return_dim', (1, 2, None))
    @pytest.mark.parametrize('strip', (True, )) # False))
    @pytest.mark.parametrize('replace', (None, ((re.compile(r'\d'), ''),)))
    @pytest.mark.parametrize('remove', (None, ('\n', '\r', '\t')))
    @pytest.mark.parametrize('normalize', (True, False, None))
    @pytest.mark.parametrize('lexicon_lookup', (None, {'auto_delete': True}))
    @pytest.mark.parametrize('remove_stops', (True, )) # False))
    @pytest.mark.parametrize('ngram_merge',
        (None, {'ngrams': [['buffalo', 'chicken']], 'wrap':False})
    )
    @pytest.mark.parametrize('justify', (None, 79))
    @pytest.mark.parametrize('get_statistics', (None, {'before':None, 'after':True}))
    def test_passes_all_good(
        self, _X1, _X2, _X_dim, global_sep, case_sensitive, global_flags,
        remove_empty_rows, return_dim, strip, replace, remove, normalize,
        lexicon_lookup, remove_stops, ngram_merge, justify, get_statistics
    ):

        assert _validation(
            _X1 if _X_dim == 1 else _X2,
            global_sep,
            case_sensitive,
            global_flags,
            remove_empty_rows,
            return_dim,
            strip,
            replace,
            remove,
            normalize,
            lexicon_lookup,
            remove_stops,
            ngram_merge,
            justify,
            get_statistics
    ) is None











