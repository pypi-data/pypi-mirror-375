# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._AutoTextCleaner._validation._lexicon_lookup \
    import _val_lexicon_lookup

import pytest



class TestValLexiconLookup:


    @pytest.mark.parametrize('_junk_ll',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    def test_rejects_junk(self, _junk_ll):

        with pytest.raises(TypeError):

            _val_lexicon_lookup(_junk_ll)


    @pytest.mark.parametrize('_bad_ll',
        ({'trash': True}, {'garbage':True, 'before':None, 'after':None}))
    def test_rejects_bad(self, _bad_ll):

        with pytest.raises(ValueError):

            _val_lexicon_lookup(_bad_ll)


    def test_accepts_good(self):

        assert _val_lexicon_lookup(None) is None

        _good_ll = {
            'update_lexicon': False,
            'skip_numbers': True,
            'auto_split': True,
            'auto_add_to_lexicon': False,
            'auto_delete': False,
            'DELETE_ALWAYS': None,
            'REPLACE_ALWAYS': None,
            'SKIP_ALWAYS': None,
            'SPLIT_ALWAYS': None,
            'remove_empty_rows': False,
            'verbose': False
        }

        assert _val_lexicon_lookup(_good_ll) is None















