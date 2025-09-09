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



# Run an operation with TextJustifier, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TJ = TextJustifier(n_chars=15)
        out = TJ.fit_transform([['A', 'SORRY', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'SORRY', 'LIST'])
        assert np.array_equal(out[1], ['OF', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('SORRY', 'LIST'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'SORRY_LIST'])
        assert np.array_equal(out2[1], ['OF', 'WORDS'])


    def test_stopremover(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['TWELVE', 'METER', 'PAPER'])
        assert np.array_equal(out[1], ['LIST', 'OF', 'WORDS'])

        TestCls = StopRemover(supplemental=['PAPER', 'WORDS'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['TWELVE', 'METER'])
        assert np.array_equal(out2[1], ['LIST'])


    def test_text_joiner(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS'])

        TestCls = TextJoiner(sep='&')
        out2 = TestCls.fit_transform(out)

        assert out2[0] == 'ANOTHER&LIST&OF'
        assert out2[1] == 'WORDS'


    def test_text_justifier(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['WORDS'])

        TestCls = TextJustifier(n_chars=10)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER'])
        assert np.array_equal(out2[1], ['LIST', 'OF'])
        assert np.array_equal(out2[2], ['WORDS'])


    def test_text_lookup(self):

        TJ = TextJustifier(n_chars=15)
        out = TJ.fit_transform([['A', 'LOT', 'OF', 'DLFKLF', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF'])
        assert np.array_equal(out[1], ['DLFKLF', 'WORDS'])

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF'])
        assert np.array_equal(out2[1], ['WORDS'])


    def test_text_lookuprealtime(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['MORE', 'OF', 'FRIED', 'DFDFAFAS', 'SALAD']])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED'])
        assert np.array_equal(out[1], ['DFDFAFAS', 'SALAD'])

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'FRIED'])
        assert np.array_equal(out2[1], ['SALAD'])


    def test_text_normalizer(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['MORE', 'DEEP', 'FRIED', 'LONG', 'WORDS']])

        assert np.array_equal(out[0], ['MORE', 'DEEP', 'FRIED'])
        assert np.array_equal(out[1], ['LONG', 'WORDS'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['more', 'deep', 'fried'])
        assert np.array_equal(out2[1], ['long', 'words'])


    def test_text_padder(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform(
            [['LONG', 'LIST', 'SILLY', 'WORDS', 'ABOUT']]
        )

        assert np.array_equal(out[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out[1], ['WORDS', 'ABOUT'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out2[1], ['WORDS', 'ABOUT', 'NULL'])


    def test_text_remover(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['THIS', 'CRAZY', 'LONG'])
        assert np.array_equal(out[1], ['SALAD', 'SHOOTER'])

        TestCls = TextRemover(remove=('CRAZY', 'SHOOTER'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['THIS', 'LONG'])
        assert np.array_equal(out2[1], ['SALAD'])


    def test_text_replacer(self):

        TJ = TextJustifier(n_chars=15)
        out = TJ.fit_transform([['A', 'LIST', 'OF', 'FILTHY', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'LIST', 'OF'])
        assert np.array_equal(out[1], ['FILTHY', 'WORDS'])

        TestCls = TextReplacer(replace=(('FILTHY', 'HOLY'), ('WORDS', 'BOOKS')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LIST', 'OF'])
        assert np.array_equal(out2[1], ['HOLY', 'BOOKS'])


    def test_text_splitter(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform(['ANOTHER SEQUENCE OF WORDS'])

        assert out[0] == 'ANOTHER SEQUENCE OF '
        assert out[1] == 'WORDS'

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'SEQUENCE', 'OF', ''])
        assert np.array_equal(out2[1], ['WORDS'])


    def test_text_stripper(self):

        TJ = TextJustifier(n_chars=20)
        out = TJ.fit_transform([['A', 'VERY', '   LONG', 'LIST', 'OF   ', 'WORDS']])

        assert np.array_equal(out[0], ['A', 'VERY', '', '', '', 'LONG', 'LIST'])
        assert np.array_equal(out[1], ['OF', '', '', '', 'WORDS'])

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'VERY', '', '', '', 'LONG', 'LIST'])
        assert np.array_equal(out2[1], ['OF', '', '', '', 'WORDS'])



