# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.feature_extraction.text.__shared._param_conditioner. \
    _compile_maker import _compile_maker

import pytest

import random
import re

import numpy as np



class TestCompileMaker:

    # shouldnt ever see None (unless in a list)
    # any str literal is converted to re.compile
    # always returns a list


    def test_rejects_None(self):

        with pytest.raises(TypeError):
            _compile_maker(
                _pattern_holder=None,
                _order_matters=False,
                _n_rows=5,
                _name='whatever'
            )


    @pytest.mark.parametrize('order_matters', (True, False))
    @pytest.mark.parametrize('n_rows', (3, 5))

    def test_accuracy(self, order_matters, n_rows):

        # 'str'
        _pattern_holder = 'abc'
        out = _compile_maker(
            _pattern_holder, order_matters, n_rows, _name='str test'
        )

        # 'order_matters' wont matter on str
        assert isinstance(out, list)
        assert len(out) == n_rows
        for row in out:
            assert isinstance(row, list)
            assert len(row) == 1
            assert all(map(isinstance, row, (re.Pattern for _ in row)))
            assert all(x.pattern == 'abc' for x in row)

        # str is escaped -- 'order_matters' still wont matter!
        out = _compile_maker('^\n\s\t$', order_matters, n_rows)
        for row in out:
            assert row[0].pattern == re.escape('^\n\s\t$')

        ##################################################################

        # 're.Pattern'
        _pattern_holder = re.compile('abc')
        assert isinstance(_pattern_holder, re.Pattern)
        assert _pattern_holder.pattern == 'abc'

        out = _compile_maker(
            _pattern_holder, order_matters, n_rows, 're.compile test'
        )

        # 'order_matters' wont matter on re.compile
        assert isinstance(out, list)
        assert len(out) == n_rows
        for row in out:
            assert isinstance(row, list)
            assert len(row) == 1
            assert all(map(isinstance, row, (re.Pattern for _ in row)))
            assert all(x.pattern == 'abc' for x in row)

        # dont need to worry about re.escape here, user should have done it

        ##################################################################

        # 'tuple'

        # 'order_matters' matters!

        # no duplicates --- should return all str/patterns in _pattern_holder,
        # if 'order_matters', the order must be correct, otherwise doesnt matter
        _len = random.choice(range(2, 5))
        _pattern_holder = [
            r'^\n\s\t$', re.compile('def'), 'ghi', re.compile('jkl'), 'mno'
        ][:_len]
        _pattern_holder = tuple(_pattern_holder)
        assert isinstance(_pattern_holder, tuple)
        assert all(map(
            isinstance,
            _pattern_holder,
            ((str, re.Pattern) for _ in _pattern_holder)
        ))

        out = _compile_maker(
            _pattern_holder, order_matters, n_rows, _name='tuple no duplicates'
        )

        assert isinstance(out, list)
        assert len(out) == n_rows
        for row in out:
            assert isinstance(row, list)
            assert len(row) == _len
            assert all(map(isinstance, row, (re.Pattern for _ in row)))
            _ref = []
            for idx, thing in enumerate(_pattern_holder):
                try:
                    _ref.append(re.escape(thing))
                except:
                    _ref.append(thing.pattern)
            if order_matters:
                assert np.array_equal([x.pattern for x in row], _ref)
            else:
                assert np.array_equal(sorted([x.pattern for x in row]), sorted(_ref))

        # duplicates --- should reduce down to 1 unique when 'order_matters' is
        # False, but when True should not be changed
        _len = random.choice(range(2, 5))
        _pattern_holder = [
            'abc', re.compile('abc'), 'abc', re.compile('abc'), 'abc'
        ][:_len]
        _pattern_holder = tuple(_pattern_holder)
        assert isinstance(_pattern_holder, tuple)
        assert all(map(
            isinstance,
            _pattern_holder,
            ((str, re.Pattern) for _ in _pattern_holder)
        ))

        out = _compile_maker(
            _pattern_holder, order_matters, n_rows, _name='tuple w duplicates'
        )

        assert isinstance(out, list)
        assert len(out) == n_rows
        for row in out:
            assert isinstance(row, list)
            assert all(map(isinstance, row, (re.Pattern for _ in row)))
            if order_matters:
                assert len(row) == _len
                assert np.array_equal(
                    [x.pattern for x in row],
                    ['abc' for _ in range(_len)]
                )
            else:
                assert len(row) == 1
                assert np.array_equal(
                    [x.pattern for x in row],
                    ['abc']
                )

        ##################################################################

        # 'list'

        _pattern_holder = [
            r'^\n\s\t$',
            re.compile('def'),
            ('ghi', re.compile('ghi')),
            None,
            'abc'
        ][:n_rows]

        # there is a tuple in here so 'order_matters' matters!

        out = _compile_maker(
            _pattern_holder, order_matters, n_rows, _name='list test'
        )

        assert isinstance(out, list)
        assert len(out) == n_rows
        for _idx, row in enumerate(out):
            assert isinstance(row, list)
            if _pattern_holder[_idx] is None:
                assert row == [None]
            elif isinstance(_pattern_holder[_idx], str):
                assert isinstance(row, list)
                assert len(row) == 1
                assert isinstance(row[0], re.Pattern)
                assert row[0].pattern == re.escape(_pattern_holder[_idx])
            elif isinstance(_pattern_holder[_idx], tuple):
                assert isinstance(row, list)
                assert all(map(isinstance, row, (re.Pattern for _ in row)))
                if order_matters:
                    assert len(row) == len(_pattern_holder[_idx])
                    assert np.array_equal(
                        [x.pattern for x in row],
                        ['ghi' for _ in range(len(_pattern_holder[_idx]))]
                    )
                else:
                    assert len(row) == 1
                    assert np.array_equal(
                        [x.pattern for x in row],
                        ['ghi']
                    )

        # ##################################################################










