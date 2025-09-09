# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.base._check_scipy_sparse import check_scipy_sparse

import numpy as np
import pandas as pd
import polars as pl
import scipy.sparse as ss

import pytest



class TestCheckScipySparse:

    # def check_scipy_sparse(
    #     X,
    #     allowed: (
    #         Literal[False],
    #         | None,
    #         | Iterable[Literal["csr", "csc", "coo", "dia", "lil", "dok", "bsr"]]
    #     )
    # ) -> None:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # X is not validated

    @pytest.mark.parametrize('junk_allowed',
        (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', {'A':1}, lambda x: x)
    )
    def test_rejects_junk_allowed(self, junk_allowed):

        with pytest.raises(TypeError):
            check_scipy_sparse(
                np.random.randint(0, 10, (5,3)),
                junk_allowed
            )


    @pytest.mark.parametrize('bad_allowed',
        (list('abcdefg'), tuple('1234'), set('MNOPQ'))
    )
    def test_rejects_bad_allowed(self, bad_allowed):

        with pytest.raises(ValueError):
            check_scipy_sparse(
                np.random.randint(0, 10, (5,3)),
                bad_allowed
            )


    @pytest.mark.parametrize('good_allowed',
        (
            list(('csr', 'dok', 'lil')),
            tuple(('bsr', 'csc', 'coo')),
            set(('dia', 'csr', 'csc')),
            False,
            None
        )
    )
    def test_rejects_junk_allowed(self, good_allowed):

        check_scipy_sparse(
            np.random.randint(0, 10, (5,3)),
            good_allowed
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    @pytest.mark.parametrize('X_format', ('np', 'pd', 'pl', 'csr', 'coo', 'lil'))
    @pytest.mark.parametrize('allowed',
        (('lil', 'dok', 'bsr'), {'csr', 'csc', 'coo'}, None, False)
    )
    def test_accuracy(self, X_format, allowed):

        SS = ["csr", "csc", "coo", "dia", "lil", "dok", "bsr"]

        _X = np.random.randint(0, 10, (20, 10))

        if X_format == 'np':
            _X_wip = _X
        elif X_format == 'pd':
            _X_wip = pd.DataFrame(_X)
        elif X_format == 'pl':
            _X_wip = pl.from_numpy(_X)
        elif X_format == 'csr':
            _X_wip = ss._csr.csr_array(_X)
        elif X_format == 'csc':
            _X_wip = ss._csc.csc_array(_X)
        elif X_format == 'coo':
            _X_wip = ss._coo.coo_array(_X)
        elif X_format == 'dia':
            _X_wip = ss._dia.dia_array(_X)
        elif X_format == 'lil':
            _X_wip = ss._lil.lil_array(_X)
        elif X_format == 'dok':
            _X_wip = ss._dok.dok_array(_X)
        elif X_format == 'bsr':
            _X_wip = ss._bsr.bsr_array(_X)
        else:
            raise Exception


        if X_format not in SS:
            # should just flow thru and return None
            out = check_scipy_sparse(_X_wip, allowed)
            assert out is None
        else:
            if allowed in [None, False]:
                with pytest.raises(TypeError):
                    check_scipy_sparse(_X_wip, allowed)
            elif X_format in allowed:
                # an allowed ss format should return None
                out = check_scipy_sparse(_X_wip, allowed)
                assert out is None
            else:
                with pytest.raises(TypeError):
                    check_scipy_sparse(_X_wip, allowed)







