# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import numpy as np

from pybear.feature_extraction.text._NGramMerger.NGramMerger import NGramMerger
from pybear.feature_extraction.text._StopRemover.StopRemover import StopRemover
from pybear.feature_extraction.text._TextJoiner.TextJoiner import TextJoiner
from pybear.feature_extraction.text._TextJustifier.TextJustifier import TextJustifier
from pybear.feature_extraction.text._TextLookup.TextLookup import TextLookup
from pybear.feature_extraction.text._TextLookup.TextLookupRealTime import \
    TextLookupRealTime
from pybear.feature_extraction.text._TextNormalizer.TextNormalizer import TextNormalizer
from pybear.feature_extraction.text._TextPadder.TextPadder import TextPadder
from pybear.feature_extraction.text._TextRemover.TextRemover import TextRemover
from pybear.feature_extraction.text._TextReplacer.TextReplacer import TextReplacer
from pybear.feature_extraction.text._TextSplitter.TextSplitter import TextSplitter
from pybear.feature_extraction.text._TextStripper.TextStripper import TextStripper



# Run an operation with TextLookup, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'HUBGUMP': 'LIST'}
        )
        out = TL.fit_transform([['A', 'SORRY', 'HUBGUMP', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'SORRY', 'LIST', 'OF', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('SORRY', 'LIST'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'SORRY_LIST', 'OF', 'WORDS'])


    def test_stopremover(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            SPLIT_ALWAYS={'PUVVY': ['A', 'BORING']}
        )
        out = TL.fit_transform([['PUVVY', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'BORING', 'LIST', 'OF', 'WORDS'])

        TestCls = StopRemover()
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['BORING', 'LIST', 'WORDS'])


    def test_text_joiner(self):

        TL = TextLookup(update_lexicon=False, auto_delete=True)
        out = TL.fit_transform([['ANOTHER', 'QUAMBOR', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'OF', 'WORDS'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert out2[0] == 'ANOTHER OF WORDS'


    def test_text_justifier(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True, DELETE_ALWAYS=['JOPPLE']
        )
        out = TL.fit_transform([['A', 'LOT', 'OF', 'JOPPLE', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'WORDS'])

        TestCls = TextJustifier(n_chars=10, sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF'])
        assert np.array_equal(out2[1], ['WORDS'])


    def test_text_lookup(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'KOLKOVA': 'YOCKTAR'}
        )
        out = TL.fit_transform([['HOME', 'OF', 'FRIED', 'KOLKOVA', 'SALAD']])

        assert np.array_equal(out[0], ['HOME', 'OF', 'FRIED', 'YOCKTAR', 'SALAD'])

        TestCls = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'YOCKTAR': 'MABLARK'}
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['HOME', 'OF', 'FRIED', 'MABLARK', 'SALAD'])


    def test_text_lookuprealtime(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'KOLKOVA': 'YOCKTAR'}
        )
        out = TL.fit_transform([['HOME', 'OF', 'FRIED', 'KOLKOVA', 'SALAD']])

        assert np.array_equal(out[0], ['HOME', 'OF', 'FRIED', 'YOCKTAR', 'SALAD'])

        TestCls = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'YOCKTAR': 'MABLARK'}
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['HOME', 'OF', 'FRIED', 'MABLARK', 'SALAD'])


    def test_text_normalizer(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'oggapap': 'wilrak'}
        )
        out = TL.fit_transform([['HOW', 'MUCH', 'oggapap', 'SALAD']])

        assert np.array_equal(out[0], ['HOW', 'MUCH', 'wilrak', 'SALAD'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['how', 'much', 'wilrak', 'salad'])


    def test_text_padder(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'LOFFID':'NUMSA'}
        )
        out = TL.fit_transform(
            [['LONG', 'LIST', 'SILLY'], ['WORDS', 'LOFFID']]
        )

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out[1], ['WORDS', 'NUMSA'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out2[1], ['WORDS', 'NUMSA', 'NULL'])


    def test_text_remover(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'JOPPLE': 'MAMMOTH'}
        )
        out = TL.fit_transform([['THIS', 'CRAZY', 'JOPPLE', 'SHOOTER']])

        assert np.array_equal(out[0], ['THIS', 'CRAZY', 'MAMMOTH', 'SHOOTER'])

        TestCls = TextRemover(remove=('CRAZY', 'MAMMOTH'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['THIS', 'SHOOTER'])


    def test_text_replacer(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'HOBGUMP': 'SPODDLE'}
        )
        out = TL.fit_transform([['A', 'LIST', 'OF', 'HOBGUMP', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LIST', 'OF', 'SPODDLE', 'WORDS'])

        TestCls = TextReplacer(replace=(('SPODDLE', 'MIMMBLY'),))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LIST', 'OF', 'MIMMBLY', 'WORDS'])


    def test_text_splitter(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'LUTTERN': 'SAFFINK'}
        )
        out = TL.fit_transform([['ANOTHER', 'LUTTERN', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'SAFFINK', 'OF', 'WORDS'])

        # splitter needs 1D, TextLookup can only
        joined = TextJoiner(sep=' ').fit_transform(out)

        assert joined[0] == 'ANOTHER SAFFINK OF WORDS'

        TestCls = TextSplitter(sep=' ')
        out2 = TestCls.fit_transform(joined)

        assert np.array_equal(out2[0], ['ANOTHER', 'SAFFINK', 'OF', 'WORDS'])


    def test_text_stripper(self):

        TL = TextLookup(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'BEAMUK': '   MIRIFID   '},
            SKIP_ALWAYS=['   OF  ']
        )
        out = TL.fit_transform([['A', 'BEAMUK', 'LIST', '   OF  ', 'WORDS']])

        assert np.array_equal(
            out[0], ['A', '   MIRIFID   ', 'LIST', '   OF  ', 'WORDS']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'MIRIFID', 'LIST', 'OF', 'WORDS'])




