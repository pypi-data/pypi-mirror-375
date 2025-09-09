# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#


# this is not directly tested for the MCT method. see repr_instructions_test.
# MCT.print_instructions() calls _repr_instructions().



import pytest

import numpy as np

from pybear.preprocessing._MinCountTransformer.MinCountTransformer import \
    MinCountTransformer as MCT



class TestPrintInstructionDoesntMutateFutureResults:


    def test_print_instructions(self, _shape, _kwargs):


        _count_threshold = _shape[0] // 10

        # build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        # find an X where some, but not all, rows are chopped
        ctr = 0
        while True:

            ctr += 1

            _X_np = np.random.randint(0, _count_threshold - 1, _shape)

            try:
                # will except if all rows are deleted
                TRFM_X = MCT(**_kwargs).fit_transform(_X_np)
                assert TRFM_X.shape[0] < _shape[0]
                break
            except Exception:
                if ctr == 200:
                    raise Exception(f"could not make good X in 200 tries")
                continue
        # END build X -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


        _kwargs['count_threshold'] = _count_threshold
        _kwargs['ignore_non_binary_integer_columns'] = False
        _kwargs['ignore_columns'] = [0, 1]
        _kwargs['handle_as_bool'] = [2, 3]
        _MCT = MCT(**_kwargs)

        FIRST_TRFM_X = _MCT.fit_transform(_X_np.copy())

        out1 = _MCT.print_instructions(clean_printout=False)
        out2 = _MCT.print_instructions(clean_printout=False)

        SECOND_TRFM_X = _MCT.transform(_X_np.copy())

        out3 = _MCT.print_instructions(clean_printout=False)

        assert np.array_equal(out1, out2)
        assert np.array_equal(out1, out3)
        assert np.array_equal(FIRST_TRFM_X, SECOND_TRFM_X)





