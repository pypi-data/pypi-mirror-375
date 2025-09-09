# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause


import pytest

import os
import sys

from pybear.utilities._get_module_name import get_module_name



class TestRejectsAnythingThatIsNotASysModulesString:

    @pytest.mark.parametrize(
        'string',
        (0, 1, 3.14, (), (1,2), [], [1,2], {}, {1,2}, {'a':1}, None, True, int)
    )
    def test_rejects_junk_characters(self, string):
        with pytest.raises(ValueError):
            get_module_name(string)

    def test_rejects_a_junk_string(self):
        with pytest.raises(ValueError):
            get_module_name('four_score_and_seven_years_ago')

    def test_rejects_a_foreign_path(self):
        with pytest.raises(ValueError):
            get_module_name(os.path.join('some','unknown','place','junk.py'))


def test_accepts_a_good_sys_modules_string():
    assert get_module_name(str(sys.modules[__name__])) == 'get_module_name_test'


















