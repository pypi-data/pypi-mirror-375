# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import random
import re

from pybear.feature_extraction.text.__shared._validation._pattern_holder \
    import _val_pattern_holder



class TestValPatternHolder:


    @pytest.mark.parametrize('junk_single_remove',
        (-2.7, -1, 0, 1, 2.7, True, False, lambda x: x)
    )
    def test_rejects_junk_single_remove(self, junk_single_remove):
        # could be None, str, or re.Pattern
        with pytest.raises(TypeError):
            _val_pattern_holder(junk_single_remove, 5)


    @pytest.mark.parametrize('good_single_remove',
        (None, 'something', re.compile('[a-m]*'), re.compile('[a-m]+'))
    )
    def test_accepts_good_single_remove(self, good_single_remove):
        # could be None, str, re.Pattern

        _val_pattern_holder(good_single_remove, 100_000)

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_tuple_remove',
        ((-2.7, -1, 0, 1, 2.7,), (True, False), ({1,2}, ), ({'A': 1}, ),
         (lambda x: x,), ('abc', 1), (None, list('abc')))
    )
    def test_rejects_junk_tuple_remove(self, junk_tuple_remove):
        # could be tuple[str | re.Pattern]
        with pytest.raises(TypeError):
            _val_pattern_holder(junk_tuple_remove, 5)


    @pytest.mark.parametrize('good_tuple_remove',
        (('something', re.compile('[a-m]*')), (re.compile('[a-m]+'), 'one', 'two'),
         ('abc', re.compile('^[0-9]+$'), re.compile('xyz')))
    )
    def test_accepts_good_tuple_remove(self, good_tuple_remove):
        # could be tuple[str | re.Pattern]

        _val_pattern_holder(good_tuple_remove, 5)

    # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @pytest.mark.parametrize('junk_list_remove',
        ([True, re.compile('[a-q]')], [re.compile('[1-3]'), 0], [0,1],
         [re.compile('a'), False])
    )
    def test_rejects_junk_regexp_as_list(self, junk_list_remove):
        # could be str, re.Pattern, or list[of the 2]

        with pytest.raises(TypeError):
            _val_pattern_holder(junk_list_remove, 2)


    def test_rejects_bad_remove_as_list(self):

        # too long
        with pytest.raises(ValueError):
            _val_pattern_holder([r'\W' for _ in range(6)], 5)

        # too short
        with pytest.raises(ValueError):
            _val_pattern_holder([r'\W' for _ in range(4)], 5)


    def test_accepts_good_list(self):

        _pool = [None, 'some string', re.compile('^[a-zA-Z0-9]+$'),
                 re.compile('a{0, 2}'), (re.compile('[a-d]*'), r'\W', r'\d')]

        for trial in range(20):

            _remove = [random.choice(_pool) for i in 'aaaaa']

            assert _val_pattern_holder(_remove, 5) is None










