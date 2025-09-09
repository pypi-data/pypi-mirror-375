# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text._AutoTextCleaner._validation._ngram_merge \
    import _val_ngram_merge

import pytest



class TestValNGramMerge:


    @pytest.mark.parametrize('junk_ngm',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', [0,1], (1,), {1,2}, lambda x: x)
    )
    def test_rejects_junk(self, junk_ngm):

        # can be None or dict

        with pytest.raises(TypeError):
            _val_ngram_merge(junk_ngm)


    @pytest.mark.parametrize('bad_ngm_key_1',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', 'garbage', 'rubbish')
    )
    @pytest.mark.parametrize('bad_ngm_key_2',
        (-2.7, -1, 0, 1, 2.7, True, False, 'trash', 'garbage', 'rubbish')
    )
    def test_rejects_bad_keys(self, bad_ngm_key_1, bad_ngm_key_2):

        # must be keyed with 'ngrams' and 'wrap'

        with pytest.raises(ValueError):
            _val_ngram_merge(
                {bad_ngm_key_1: (('a','b'),), bad_ngm_key_2: True}
            )


    @pytest.mark.parametrize('bad_ngm_value_1',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    @pytest.mark.parametrize('bad_ngm_value_2',
        (-2.7, -1, 0, 1, 2.7, None, 'trash', [0,1], (1,), {1,2}, {'a':1}, lambda x: x)
    )
    def test_rejects_bad_values(self, bad_ngm_value_1, bad_ngm_value_2):

        # 'ngrams' must be Seq[Seq[str/re.compile]] and 'wrap' must be bool

        with pytest.raises(TypeError):
            _val_ngram_merge(
                {'ngrams': bad_ngm_value_1, 'wrap': bad_ngm_value_2}
            )


    def test_accepts_good(self):

        assert _val_ngram_merge(None) is None

        assert _val_ngram_merge({'ngrams': (('a', 'b'),), 'wrap':True}) is None






