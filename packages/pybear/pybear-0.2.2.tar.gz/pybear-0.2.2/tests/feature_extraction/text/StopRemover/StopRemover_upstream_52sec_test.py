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



# Run an operation with StopRemover, then test all the other text modules are
# able to do an operation on mutated output as expected.



class TestUpstreamImpactOnLaterModules:


    def test_ngram_merger(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['A', 'SORRY', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['SORRY', 'LIST', 'WORDS'])

        TestClass = NGramMerger(ngrams=(('LIST', 'WORDS'),), sep='_')

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['SORRY', 'LIST_WORDS'])


    def test_stop_remover(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['A', 'SORRY', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['SORRY', 'LIST', 'WORDS'])

        TestClass = StopRemover(n_jobs=1, supplemental=['SORRY', 'LIST'])

        out2 = TestClass.fit_transform(out)

        assert np.array_equal(out2[0], ['WORDS'])


    def test_text_joiner(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['ANOTHER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['ANOTHER', 'LIST', 'WORDS'])

        TestCls = TextJoiner(sep='&')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2, ['ANOTHER&LIST&WORDS'])


    def test_text_justifier(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['TWELVE', 'METER', 'PAPER', 'LIST', 'OF', 'WORDS']])

        assert np.array_equal(out[0], ['TWELVE', 'METER', 'PAPER', 'LIST', 'WORDS'])

        TestCls = TextJustifier(n_chars=20)
        out2 = TestCls.fit_transform(out)

        assert all(map(
            np.array_equal,
            out2,
            [['TWELVE', 'METER', 'PAPER'], ['LIST', 'WORDS']]
        ))


    def test_text_lookup(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['A', 'LOT', 'OF', 'DLFKSJDLF', 'WORDS']])

        assert np.array_equal(out[0], ['LOT', 'DLFKSJDLF', 'WORDS'])

        TestCls = TextLookup(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LOT', 'WORDS'])


    def test_text_lookuprealtime(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['MORE', 'OF', 'FRIED', 'DFDFAFAS', 'SALAD']])

        assert np.array_equal(out[0], ['FRIED', 'DFDFAFAS', 'SALAD'])

        TestCls = TextLookupRealTime(update_lexicon=False, auto_delete=True)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['FRIED', 'SALAD'])


    def test_text_normalizer(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['MORE', 'DEEP', 'FRIED', 'LONG', 'WORDS']])

        assert np.array_equal(out[0], ['DEEP', 'FRIED', 'WORDS'])

        TestCls = TextNormalizer(upper=False)
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['deep', 'fried', 'words'])


    def test_text_padder(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform(
            [['LONG', 'LIST'], ['SILLY', 'WORDS', 'ABOUT']]
        )

        assert np.array_equal(out[0], ['LIST'])
        assert np.array_equal(out[1], ['SILLY', 'WORDS'])

        TestCls = TextPadder(fill='NULL')
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LIST', 'NULL'])
        assert np.array_equal(out2[1], ['SILLY', 'WORDS'])


    def test_text_remover(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform([['THIS', 'CRAZY', 'LONG', 'SALAD', 'SHOOTER']])

        assert np.array_equal(out[0], ['CRAZY', 'SALAD', 'SHOOTER'])

        TestCls = TextRemover(remove=('SALAD', 'SHOOTER'))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['CRAZY'])


    def test_text_replacer(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform(
            [['A', 'LIST', 'OF', 'FILTHY', 'WORDS']]
        )

        assert np.array_equal(out[0], ['LIST', 'FILTHY', 'WORDS'])

        TestCls = TextReplacer(replace=(('FILTHY', 'HOLY'),('WORDS', 'BOOKS')))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['LIST', 'HOLY', 'BOOKS'])


    def test_text_splitter(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform(
            [['ANOTHER', 'SEQUENCE', 'A', 'AT', 'OF', 'WORDS']]
        )

        # need to convert to 1D, TextSplitter requires 1D
        out = TextJoiner(sep=' ').fit_transform(out)

        assert np.array_equal(out, ['ANOTHER SEQUENCE WORDS'])

        TestCls = TextSplitter(sep=(' ', '='))
        out2 = TestCls.fit_transform(out)

        assert np.array_equal(out2[0], ['ANOTHER', 'SEQUENCE', 'WORDS'])


    def test_text_stripper(self):

        SR = StopRemover(n_jobs=1)
        out = SR.fit_transform(
            [['A', 'VERY', '   LONG', 'LIST', 'OF   ', 'WORDS']]
        )

        assert np.array_equal(
            out[0], ['   LONG',  'LIST', 'OF   ',  'WORDS']
        )

        out2 = TextStripper().fit_transform(out)

        assert np.array_equal(
            out2[0], ['LONG', 'LIST', 'OF', 'WORDS']
        )






