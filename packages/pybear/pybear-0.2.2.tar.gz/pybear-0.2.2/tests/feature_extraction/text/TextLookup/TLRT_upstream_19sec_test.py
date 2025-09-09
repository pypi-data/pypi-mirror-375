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



# Run an operation with TextLookupRealTime, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'ONJAID':'SHORT'}
        )
        out = TLRT.fit_transform([['A', 'ONJAID', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'SHORT', 'LIST', 'OF', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('SHORT', 'LIST'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'SHORT_LIST', 'OF', 'WORDS'])


    def test_stopremover(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'WORDS': 'PAPER'}
        )
        out = TLRT.fit_transform([['YOUR', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['YOUR', 'LIST', 'OF', 'PAPER'])

        TestCls = StopRemover(supplemental=['PAPER'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LIST'])


    def test_text_joiner(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'WORDS': 'PAPER'}
        )
        out = TLRT.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF', 'PAPER'])

        TestCls = TextJoiner(sep='&')
        out2 = TestCls.fit_transform(out)

        assert out2[0] == 'ANOTHER&LIST&OF&PAPER'


    def test_text_lookup(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'KAILARB': 'ERNLOCA'}
        )
        out = TLRT.fit_transform([['A', 'LOT', 'OF', 'KAILARB', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'ERNLOCA', 'WORDS'])

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF', 'WORDS'])


    def test_text_lookuprealtime(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'KAILARB': 'ERNLOCA'}
        )
        out = TLRT.fit_transform([['MORE', 'OF', 'FRIED', 'KAILARB', 'SALAD']])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED', 'ERNLOCA', 'SALAD'])

        TestCls = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'SALAD': 'JIBBLEJIB'}
        )
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'FRIED', 'JIBBLEJIB'])


    def test_text_normalizer(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'AMALGAM': 'FRENCH'}
        )
        out = TLRT.fit_transform([['A', 'LIST', 'OF', 'AMALGAM', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LIST', 'OF', 'FRENCH', 'WORDS'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['a', 'list', 'of', 'french', 'words'])


    def test_text_padder(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'LIOLATIK': 'NIFFERFIL'}
        )
        out = TLRT.fit_transform(
            [['LONG', 'LIST', 'SILLY', 'WORDS'],
             ['TOO', 'MANY', 'LIOLATIK'],
             ['HELP', 'US']]
        )

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY', 'WORDS'])
        assert np.array_equal(out[1], ['TOO', 'MANY', 'NIFFERFIL'])
        assert np.array_equal(out[2], ['HELP', 'US'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'SILLY', 'WORDS'])
        assert np.array_equal(out2[1], ['TOO', 'MANY', 'NIFFERFIL', 'NULL'])
        assert np.array_equal(out2[2], ['HELP', 'US', 'NULL', 'NULL'])


    def test_text_remover(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'SALAD': 'TUMMELFIP'}
        )
        out = TLRT.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(
            out[0], ['THIS', 'CRAZY', 'LONG', 'TUMMELFIP', 'SHOOTER']
        )

        TestCls = TextRemover(remove=('TUMMELFIP', 'SHOOTER'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['THIS', 'CRAZY', 'LONG'])


    def test_text_replacer(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'SALAD': 'TUMMELFIP'}
        )
        out = TLRT.fit_transform([['A', 'LIST', 'OF', 'FILTHY', 'SALAD']])

        assert np.array_equal(out[0], ['A', 'LIST', 'OF', 'FILTHY', 'TUMMELFIP'])

        TestCls = TextReplacer(replace=(('FILTHY', 'HOLY'), ('TUMMELFIP', 'BOOKS')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LIST', 'OF', 'HOLY', 'BOOKS'])


    def test_text_splitter(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'SALAD': 'RUMPELBUMP'}
        )
        out = TLRT.fit_transform([['ANOTHER', 'SEQUENCE', 'OF', 'SALAD']])

        assert np.array_equal(out[0], ['ANOTHER', 'SEQUENCE', 'OF', 'RUMPELBUMP'])

        joined = TextJoiner(sep=' ').fit_transform(out)
        assert np.array_equal(joined, ['ANOTHER SEQUENCE OF RUMPELBUMP'])

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(joined)

        assert np.array_equal(out2[0], ['ANOTHER', 'SEQUENCE', 'OF', 'RUMPELBUMP'])


    def test_text_stripper(self):

        TLRT = TextLookupRealTime(
            update_lexicon=False, auto_delete=True,
            REPLACE_ALWAYS={'WORDS': '  FLOWERS  '}
        )
        out = TLRT.fit_transform([['A', 'LONG', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LONG', 'LIST', 'OF', '  FLOWERS  '])

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LONG', 'LIST', 'OF', 'FLOWERS'])




