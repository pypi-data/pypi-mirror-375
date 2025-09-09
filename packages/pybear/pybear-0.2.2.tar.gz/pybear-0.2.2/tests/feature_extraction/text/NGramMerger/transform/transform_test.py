# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._NGramMerger._transform._transform import \
    _transform



class TestTransformNoWrap:


    # def _transform(
    #     _X: list[list[str]],
    #     _ngrams: Sequence[Sequence[str | re.Pattern]],
    #     _ngcallable: Callable[[Sequence[str]], str] | None,
    #     _sep: str | None
    # ) -> list[list[str]]:


    @pytest.mark.parametrize('_callable, _sep', (
        (None, None),
        (lambda x: "%".join(x), None),
        (None, '@'),
        (None, '&'),
        (None, '__')
    ))
    def test_accuracy_no_wrap(self, _callable, _sep):


        _text = [
            ['NEW', 'YORK', 'CITY', 'NEW', 'YORK'],
            ['FRIED', 'RICE', 'AND', 'MOO', 'GOO', 'GAI', 'PAN'],
            ['BEWARE', 'OF', 'DOG']
        ]


        _ngrams = [
            tuple(map(re.compile, ('AND', 'MOO'))),
            tuple(map(re.compile, ('YORK', 'FRIED'))),
            tuple(map(re.compile, ('NEW', 'YORK', 'CITY'))),
            tuple(map(re.compile, ('FRIED', 'RICE'))),
            tuple(map(re.compile, ('MOO', 'GOO', 'GAI', 'PAN')))
        ]


        if _callable is not None:
            _exp_sep = '%'
        else:
            _exp_sep = _sep or '_'


        out, row_support = _transform(_text, _ngrams, _callable, _sep, False, False)

        # new_york_city must trump new_york

        exp = [
            [f'NEW{_exp_sep}YORK{_exp_sep}CITY', 'NEW', 'YORK'],
            [f'FRIED{_exp_sep}RICE', 'AND',
             f'MOO{_exp_sep}GOO{_exp_sep}GAI{_exp_sep}PAN'],
            ['BEWARE', 'OF', 'DOG']
        ]

        assert isinstance(out, list)
        for _row_idx in range(len(out)):
            assert isinstance(out[_row_idx], list)
            assert all(map(isinstance, out[_row_idx], (str for _ in out[_row_idx])))
            assert np.array_equal(out[_row_idx], exp[_row_idx])

        assert np.array_equal(row_support, [True] * len(_text))


class TestTransformWithWrap1:


    @pytest.mark.parametrize('_callable, _sep', (
        (None, None),
        (lambda x: "%".join(x), None),
        (None, '@'),
        (None, '&'),
        (None, '__')
    ))
    def test_accuracy_with_wrap_1(self, _callable, _sep):


        _text = [
            ['NEW', 'YORK', 'CITY', 'NEW', 'YORK'],
            ['FRIED', 'RICE', 'AND', 'MOO', 'GOO', 'GAI', 'PAN'],
            ['BEWARE', 'OF', 'DOG']
        ]

        _ngrams = [
            tuple(map(re.compile, ('NEW', 'YORK', 'CITY'))),
            tuple(map(re.compile, ('YORK', 'FRIED'))),
            tuple(map(re.compile, ('PAN', 'BEWARE'))),
            tuple(map(re.compile, ('MOO', 'GOO', 'GAI', 'PAN')))
        ]


        # LONGEST NGRAMS RUN FIRST. MOO GOO GAI PAN WILL ALWAYS MERGE
        # BEFORE IT TRIES TO WRAP ON ('PAN', 'BEWARE'), SO THE WRAP SHOULD
        # NEVER HAPPEN. 'YORK' & 'FRIED' SHOULD ALWAYS HAPPEN.


        if _callable is not None:
            _exp_sep = '%'
        else:
            _exp_sep = _sep or '_'


        out, row_support = _transform(_text, _ngrams, _callable, _sep, True, False)

        # new_york_city must trump new_york

        exp = [
            [f'NEW{_exp_sep}YORK{_exp_sep}CITY', 'NEW', f'YORK{_exp_sep}FRIED'],
            ['RICE', 'AND', f'MOO{_exp_sep}GOO{_exp_sep}GAI{_exp_sep}PAN'],
            ['BEWARE', 'OF', 'DOG']
        ]

        assert isinstance(out, list)
        for _row_idx in range(len(out)):
            assert isinstance(out[_row_idx], list)
            assert all(map(isinstance, out[_row_idx], (str for _ in out[_row_idx])))
            assert np.array_equal(out[_row_idx], exp[_row_idx])

        assert np.array_equal(row_support, [True] * len(_text))


class TestTransformWithWrap2:


    @pytest.mark.parametrize('_callable, _sep', (
        (None, None),
        (lambda x: "%".join(x), None),
        (None, '@'),
        (None, '&'),
        (None, '__')
    ))
    def test_accuracy_with_wrap_2(self, _callable, _sep):

        # LONGEST NGRAMS RUN FIRST, THEN IN ORDER FOR EQUAL LENGTH NGRAMS.
        # 'NEW' 'YORK' WILL TRUMP 'YORK' 'FRIED' BECAUSE IT IS FIRST
        # 'PAN' 'BEWARE' WILL DO THE WRAP BEFORE 'BEWARE' 'OF' BECAUSE
        # IT IS FIRST

        _text = [
            ['NEW', 'YORK', 'CITY', 'NEW', 'YORK'],
            ['FRIED', 'RICE', 'AND', 'MOO', 'GOO', 'GAI', 'PAN'],
            ['BEWARE', 'OF', 'DOG']
        ]

        _ngrams = [
            tuple(map(re.compile, ('NEW', 'YORK', 'CITY'))),
            tuple(map(re.compile, ('NEW', 'YORK'))),
            tuple(map(re.compile, ('YORK', 'FRIED'))),
            tuple(map(re.compile, ('PAN', 'BEWARE'))),
            tuple(map(re.compile, ('BEWARE', 'OF')))
        ]


        if _callable is not None:
            _exp_sep = '%'
        else:
            _exp_sep = _sep or '_'


        out, row_support = _transform(_text, _ngrams, _callable, _sep, True, False)

        # new_york_city must trump new_york

        exp = [
            [f'NEW{_exp_sep}YORK{_exp_sep}CITY', f'NEW{_exp_sep}YORK'],
            ['FRIED', 'RICE', 'AND', 'MOO', 'GOO', 'GAI', f'PAN{_exp_sep}BEWARE'],
            ['OF', 'DOG']
        ]

        assert isinstance(out, list)
        for _row_idx in range(len(out)):
            assert isinstance(out[_row_idx], list)
            assert all(map(isinstance, out[_row_idx], (str for _ in out[_row_idx])))
            assert np.array_equal(out[_row_idx], exp[_row_idx])

        assert np.array_equal(row_support, [True] * len(_text))


class TestSingleWordsWithWrap:


    @pytest.mark.parametrize('_remove_empty_rows', (True, False))
    @pytest.mark.parametrize('_callable, _sep', (
        (None, None),
        (lambda x: "%".join(x), None),
        (None, '@'),
        (None, '&'),
        (None, '__')
    ))
    def test_accuracy(self, _callable, _sep, _remove_empty_rows):


        _text = [
            ['NEW'], ['YORK'], ['CITY'], ['NEW'], ['YORK']
        ]

        _ngrams = [
            tuple(map(re.compile, ('NEW', 'YORK', 'CITY'))),
            tuple(map(re.compile, ('NEW', 'YORK')))
        ]


        if _callable is not None:
            _exp_sep = '%'
        else:
            _exp_sep = _sep or '_'


        out, row_support = \
            _transform(_text, _ngrams, _callable, _sep, True, _remove_empty_rows)

        # new_york_city must trump new_york

        if _remove_empty_rows:
            exp = [
                [f'NEW{_exp_sep}YORK'], ['CITY'], [f'NEW{_exp_sep}YORK']
            ]
            exp_row_support = [True, False, True, True, False]
        else:
            exp = [
                [f'NEW{_exp_sep}YORK'], [], ['CITY'], [f'NEW{_exp_sep}YORK'], []
            ]
            exp_row_support = [True, True, True, True, True]


        assert isinstance(out, list)
        for _row_idx in range(len(out)):
            assert isinstance(out[_row_idx], list)
            assert all(map(isinstance, out[_row_idx], (str for _ in out[_row_idx])))
            assert np.array_equal(out[_row_idx], exp[_row_idx])

        assert np.array_equal(row_support, exp_row_support)




