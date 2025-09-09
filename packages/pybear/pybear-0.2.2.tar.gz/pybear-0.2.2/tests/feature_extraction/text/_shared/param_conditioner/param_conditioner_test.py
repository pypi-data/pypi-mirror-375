# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text.__shared._param_conditioner. \
    _param_conditioner import _param_conditioner



class TestParamConditioner:


    # no validation

    # we know the submodules that comprise _param_conditioner work because
    # of their own tests. just test that this gives the expected output.


    @pytest.mark.parametrize('_holder_format',
        ('None', 'str', 'compile', 'tuple', 'list')
    )
    @pytest.mark.parametrize('_cs', (True, False, [None, True, False, None]))
    @pytest.mark.parametrize('_order_matters', (True, False))
    @pytest.mark.parametrize('_flags', (None, re.I, [re.I, None, re.M, None]))
    def test_accuracy(self, _holder_format, _cs, _order_matters, _flags):

        _holder_as_list = [
            None,
            'remove_me',
            re.compile('take_me_out', re.I),
            ('im_a_gonner', re.compile('go_bye_bye'))
        ]

        _n_rows = len(_holder_as_list)


        if _holder_format == 'None':
            _holder = None
            _exp_out = None
        elif _holder_format == 'str':
            _holder = 'take_me_out'
            _exp_out = re.compile('take_me_out')
        elif _holder_format == 'compile':
            _holder = re.compile('go_away', re.I)
            _exp_out = re.compile('go_away', re.I)
        elif _holder_format == 'tuple':
            _holder = ('no_mas', re.compile('game_over'))
            _exp_out = (re.compile('no_mas'), re.compile('game_over'))
        elif _holder_format == 'list':
            _holder = _holder_as_list
            _exp_out = [
                None,
                re.compile('remove_me'),
                re.compile('take_me_out', re.I),
                (re.compile('im_a_gonner'), re.compile('go_bye_bye'))
            ]
        else:
            raise Exception

        # 'order_matters' shouldnt matter for any of the tuples
        out = _param_conditioner(
            _holder,
            _cs,
            _flags,
            _order_matters,
            _n_rows,
            _name='p_c_test'
        )

        # forget about the flags, we know flag_maker works right
        if _holder is None:
            assert out is None
        elif isinstance(_holder, str):
            if isinstance(out, re.Pattern):
                assert out.pattern == _exp_out.pattern
            else:  # must be list because of different flags
                for i in out:
                    assert i.pattern == _exp_out.pattern
        elif isinstance(_holder, re.Pattern):
            if isinstance(out, re.Pattern):
                assert out.pattern == _exp_out.pattern
            else:  # must be list because of different flags
                for i in out:
                    assert i.pattern == _exp_out.pattern
        elif isinstance(_holder, tuple):
            if isinstance(out, tuple):
                _out_patterns = [i.pattern for i in out]
                _exp_patterns = [j.pattern for j in _exp_out]
                assert np.array_equal(
                    sorted(_out_patterns),
                    sorted(_exp_patterns)
                )
            else:  # must be list because of different flags
                for _tuple in out:
                    _out_patterns = [i.pattern for i in _tuple]
                    _exp_patterns = [j.pattern for j in _exp_out]
                    assert np.array_equal(
                        sorted(_out_patterns),
                        sorted(_exp_patterns)
                    )
        elif isinstance(_holder, list):
            for _idx, _thing in enumerate(out):
                if _thing is None:
                    assert _exp_out[_idx] is None
                elif isinstance(_thing, re.Pattern):
                    assert _thing.pattern == _exp_out[_idx].pattern
                elif isinstance(_thing, tuple):
                    _out_patterns = [i.pattern for i in _thing]
                    _exp_patterns = [j.pattern for j in _exp_out[_idx]]
                    assert np.array_equal(
                        sorted(_out_patterns),
                        sorted(_exp_patterns)
                    )
                else:
                    raise Exception
        else:
            raise Exception





