# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import numpy as np

from pybear.feature_extraction.text._TextSplitter._validation import _validation



class TestValidation:

    # the brunt of testing validation is handled by the individual validation
    # modules' tests

    # just make sure that it accepts all good parameters, and that the
    # conditionals for passing parameters are enforced.
    # 1) cannot pass 'flags' if 'sep' is not passed
    # 2) cannot pass 'case_sensitive' as a list if 'sep' is not passed



    @pytest.mark.parametrize('X_container', (list, tuple, np.ndarray))
    @pytest.mark.parametrize('sep, sep_container',
        (
            (None, None),
            (' ', None),
            ((' ', '\n', r'\s'), None),
            ('sep_seq_1', list),
            ('sep_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('maxsplit, maxsplit_container',
        (
            (None, None),
            (0, None),
            ('maxsplit_seq_1', list),
            ('maxsplit_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('case_sensitive, case_sensitive_container',
        (
            (True, None),
            (False, None),
            ('case_sensitive_seq_1', list),
            ('case_sensitive_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('flags, flags_container',
        (
            (None, None),
            (re.I | re.X, None),
            ('flags_seq_1', list),
            ('flags_seq_1', tuple)
        )
    )
    @pytest.mark.parametrize('sep_empty_rows', (True, False, 'garbage'))
    def test_accuracy(
        self, X_container, sep, case_sensitive, maxsplit, flags, sep_empty_rows,
        sep_container, case_sensitive_container, maxsplit_container, flags_container
    ):

        _type_error = False
        _value_error = False


        _text_dim_1 = [
            'Despair thy charm, ',
            'And let the angel whom thou still hast served ',
            'Tell thee Macduff was ',
            "from his mother’s womb",
            "Untimely ripped."
        ]

        sep_seq_1 = [
            (' ', ',', re.compile(re.escape('.'))),
            '',
            re.compile(re.escape('\n')),
            r'\s',
            None
        ]

        case_sensitive_seq_1 = [False, True, True, True, None]

        maxsplit_seq_1 = [4, 0, 0, 0, 0]

        flags_seq_1 = [None, re.I, None, re.I | re.X, None]


        # manage container -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        if X_container is np.ndarray:
            _X = np.array(_text_dim_1)
        else:
            _X = X_container(_text_dim_1)
        assert isinstance(_X, X_container)
        # END manage container -- -- -- -- -- -- -- -- -- -- -- -- -- --

        # manage param containers, when applicable -- -- -- -- -- -- -- --
        if sep == 'sep_seq_1':
            sep = sep_container(sep_seq_1)
            assert isinstance(sep, sep_container)

        if case_sensitive == 'case_sensitive_seq_1':
            case_sensitive = case_sensitive_container(case_sensitive_seq_1)
            assert isinstance(case_sensitive, case_sensitive_container)

        if maxsplit == 'maxsplit_seq_1':
            maxsplit = maxsplit_container(maxsplit_seq_1)
            assert isinstance(maxsplit, maxsplit_container)

        if flags == 'flags_seq_1':
            flags = flags_container(flags_seq_1)
            assert isinstance(flags, flags_container)
        # END manage param containers, when applicable -- -- -- -- -- --

        # manage exceptions -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if isinstance(sep, tuple) and len(sep) == 5:
            # need to distinguish between the valid tuple of patterns and
            # the list of patterns wrongfully passed as a tuple
            _type_error = True

        if isinstance(case_sensitive, list) and not sep:
            _value_error = True

        if isinstance(case_sensitive, (set, tuple)):
            _type_error = True

        if isinstance(maxsplit, (set, tuple)):
            _type_error = True

        if maxsplit is not None and not sep:
            _value_error = True

        if isinstance(flags, (set, tuple)):
            _type_error = True

        if flags is not None and not sep:
            _value_error = True
        # END manage exceptions -- -- -- -- -- -- -- -- -- -- -- -- --

        # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        if _type_error or _value_error:
            with pytest.raises((TypeError, ValueError)):
                _validation(
                    _X,
                    _sep=sep,
                    _case_sensitive=case_sensitive,
                    _maxsplit=maxsplit,
                    _flags=flags
                )
        else:
            out = _validation(
                _X,
                _sep=sep,
                _case_sensitive=case_sensitive,
                _maxsplit=maxsplit,
                _flags=flags
            )

            assert out is None





