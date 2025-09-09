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



# Run an operation with TextNormalizer, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform([['a', 'sorry', 'list', 'of', 'words']])

        assert np.array_equal(out[0], ['A', 'SORRY', 'LIST', 'OF', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('SORRY', 'LIST'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'SORRY_LIST', 'OF', 'WORDS'])


    def test_stopremover(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(
            out[0], ['twelve', 'meter', 'paper', 'list', 'of', 'words']
        )

        TestCls = StopRemover(supplemental=['twelve', 'words'])
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['meter', 'paper', 'list'])


    def test_text_joiner(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['another', 'list', 'of', 'words'])

        TestCls = TextJoiner(sep=' ')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['another list of words'])


    def test_text_justifier(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform([['more', 'deep', 'fried', 'long', 'words']])

        assert np.array_equal(out[0], ['MORE', 'DEEP', 'FRIED', 'LONG', 'WORDS'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'DEEP', 'FRIED'])
        assert np.array_equal(out2[1], ['LONG', 'WORDS'])


    def test_text_lookup(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform([['a', 'lot', 'of', 'pfdslf', 'words']])

        assert np.array_equal(out[0], ['A', 'LOT', 'OF', 'PFDSLF', 'WORDS'])

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LOT', 'OF', 'WORDS'])


    def test_text_lookuprealtime(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform([['more', 'of', 'fried', 'dfdfafas', 'salad']])

        assert np.array_equal(out[0], ['MORE', 'OF', 'FRIED', 'DFDFAFAS', 'SALAD'])

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['MORE', 'OF', 'FRIED', 'SALAD'])


    def test_text_normalizer(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['LONG', 'LIST', 'SILLY'], ['WORDS', 'ABOUT']])

        assert np.array_equal(out[0], ['long', 'list', 'silly'])
        assert np.array_equal(out[1], ['words', 'about'])

        TestCls = TextNormalizer(upper=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LONG', 'LIST', 'SILLY'])
        assert np.array_equal(out2[1], ['WORDS', 'ABOUT'])


    def test_text_padder(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['LONG', 'LIST', 'SILLY'], ['WORDS', 'ABOUT']])

        assert np.array_equal(out[0], ['long', 'list', 'silly'])
        assert np.array_equal(out[1], ['words', 'about'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['long', 'list', 'silly'])
        assert np.array_equal(out2[1], ['words', 'about', 'NULL'])


    def test_text_remover(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['this', 'crazy', 'long', 'salad', 'shooter'])

        TestCls = TextRemover(remove=('crazy', 'shooter'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['this', 'long', 'salad'])


    def test_text_replacer(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform([['a', 'list', 'of', 'filthy', 'words']])

        assert np.array_equal(out[0], ['A', 'LIST', 'OF', 'FILTHY', 'WORDS'])

        TestCls = TextReplacer(replace=(('FILTHY', 'HOLY'), ('WORDS', 'BOOKS')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['A', 'LIST', 'OF', 'HOLY', 'BOOKS'])


    def test_text_splitter(self):

        TN = TextNormalizer(upper=True)
        out = TN.fit_transform(['another sequence of words'])

        assert out[0] == 'ANOTHER SEQUENCE OF WORDS'

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'SEQUENCE', 'OF', 'WORDS'])


    def test_text_stripper(self):

        TN = TextNormalizer(upper=False)
        out = TN.fit_transform([['A', 'VERY', '   LONG', 'LIST', 'OF   ', 'WORDS']])

        assert np.array_equal(
            out[0], ['a', 'very', '   long', 'list', 'of   ', 'words']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(
            out2[0], ['a', 'very', 'long', 'list', 'of', 'words']
        )



