# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._SlimPolyFeatures._partial_fit._combination_builder \
    import _combination_builder



class TestCombinationBuilder:


    @pytest.mark.parametrize('_n_features_in',
        (-1, 3.14, None, True, 'junk', [1, 2], (2, 3), {'a': 1}, lambda x: x)
    )
    def test_n_features_in_validation(self, _n_features_in):

        with pytest.raises(AssertionError):
            _combination_builder(
                n_features_in_=_n_features_in,
                _min_degree=1,
                _max_degree=2,
                _intx_only=True
            )


    @pytest.mark.parametrize('_min_degree',
        (-1, 0, 1, 3.14, None, True, 'junk', (2, 3), {'a': 1}, lambda x: x)
    )
    def test_min_degree_validation(self, _min_degree):

        if isinstance(_min_degree, int) and not isinstance(_min_degree, bool) and \
            _min_degree >= 1:

            _combination_builder(
                n_features_in_=3,
                _min_degree=_min_degree,
                _max_degree=4,
                _intx_only=False
            )

        else:
            with pytest.raises(AssertionError):
                _combination_builder(
                    n_features_in_=3,
                    _min_degree=_min_degree,
                    _max_degree=4,
                    _intx_only=False
                )


    @pytest.mark.parametrize('_max_degree',
        (-1, 0, 2, 3.14, None, True, 'junk', (2, 3), {'a': 1}, lambda x: x)
    )
    def test_max_degree_validation(self, _max_degree):

        if isinstance(_max_degree, int) and not isinstance(_max_degree, bool) and \
            _max_degree >= 2:

            _combination_builder(
                n_features_in_=10,
                _min_degree=1,
                _max_degree=_max_degree,
                _intx_only=True
            )

        else:
            with pytest.raises(AssertionError):
                _combination_builder(
                    n_features_in_=10,
                    _min_degree=1,
                    _max_degree=_max_degree,
                    _intx_only=True
                )



    @pytest.mark.parametrize('_intx_only',
        (-1, 1, 3.14, None, True, 'junk', [1, 2], (2, 3), {'a': 1}, lambda x: x)
    )
    def test_intx_only_validation(self, _intx_only):

        if isinstance(_intx_only, bool):

            _combination_builder(
                n_features_in_=3,
                _min_degree=1,
                _max_degree=3,
                _intx_only=_intx_only
            )

        else:
            with pytest.raises(AssertionError):
                _combination_builder(
                    n_features_in_=3,
                    _min_degree=1,
                    _max_degree=3,
                    _intx_only=_intx_only
                )


    @pytest.mark.parametrize('_min_degree', (0, ))
    @pytest.mark.parametrize('_max_degree', (0, 1))
    @pytest.mark.parametrize('_intx_only', (True, False))
    def test_blocks_disallowed_degrees(
        self, _min_degree, _max_degree, _intx_only
    ):

        with pytest.raises(AssertionError):
            _combination_builder(
                n_features_in_=3,
                _min_degree=_min_degree,
                _max_degree=_max_degree,
                _intx_only=_intx_only
            )


    @pytest.mark.parametrize('_intx_only', (True, False))
    def test_bumps_min_degree_one_to_two(self, _intx_only):

        # degree==1 is dealt with separately. if min_degree==1,
        # _combination_builder bumps it up to 2.

        out_one = _combination_builder(
            n_features_in_=3,
            _min_degree=1,
            _max_degree=2,
            _intx_only=_intx_only
        )

        out_two = _combination_builder(
            n_features_in_=3,
            _min_degree=2,
            _max_degree=2,
            _intx_only=_intx_only
        )

        assert list(out_one) == list(out_two)


    @pytest.mark.parametrize('_min_degree', (1, 2))
    @pytest.mark.parametrize('_max_degree', (2, 3))
    @pytest.mark.parametrize('_intx_only', (True, False))
    @pytest.mark.parametrize('_n_features', (2, 3))
    def test_accuracy(
        self, _min_degree, _max_degree, _intx_only, _n_features
    ):

        # if min_degree comes in as 1, it is bumped up to 2

        out = _combination_builder(
            n_features_in_=_n_features,
            _min_degree=_min_degree,
            _max_degree=_max_degree,
            _intx_only=_intx_only
        )

        if _n_features == 2:

            if _min_degree == 1:   # should be bumped to 2
                if _max_degree == 2:
                    if _intx_only:
                        assert list(out) == [(0, 1)]
                    elif not _intx_only:
                        assert list(out) == [(0, 0), (0, 1), (1, 1)]


                elif _max_degree == 3:
                    if _intx_only:
                        assert list(out) == [(0, 1)]

                    elif not _intx_only:
                        assert list(out) == \
                           [
                                (0, 0), (0, 1), (1, 1),
                                (0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1)
                            ]

                else:
                    raise Exception

            elif _min_degree == 2:
                if _max_degree == 2:
                    if _intx_only:
                        assert list(out) == [(0, 1)]
                    elif not _intx_only:
                        assert list(out) == [(0, 0), (0, 1), (1, 1)]
                elif _max_degree == 3:
                    if _intx_only:
                        assert list(out) == [(0, 1)]
                    elif not _intx_only:
                        assert list(out) == \
                            [
                                (0, 0), (0, 1), (1, 1), (0, 0, 0),
                                (0, 0, 1), (0, 1, 1), (1, 1, 1)
                            ]

                else:
                    raise Exception

            else:
                raise Exception

        elif _n_features == 3:

            if _min_degree == 1:
                if _max_degree == 2:
                    if _intx_only:
                        assert list(out) == [(0, 1), (0, 2), (1, 2)]
                    elif not _intx_only:
                        assert list(out) == \
                           [
                               (0, 0), (0, 1),
                               (0, 2), (1, 1), (1, 2), (2, 2)
                           ]
                elif _max_degree == 3:
                    if _intx_only:
                        assert list(out) == \
                           [
                               (0, 1), (0, 2), (1, 2), (0, 1, 2)
                           ]
                    elif not _intx_only:
                        assert list(out) == \
                           [
                               (0, 0), (0, 1), (0, 2), (1, 1), (1, 2),
                               (2, 2), (0, 0, 0), (0, 0, 1), (0, 0, 2),
                               (0, 1, 1), (0, 1, 2), (0, 2, 2), (1, 1, 1),
                               (1, 1, 2), (1, 2, 2), (2, 2, 2)
                           ]
                else:
                    raise Exception

            elif _min_degree == 2:
                if _max_degree == 2:
                    if _intx_only:
                        assert list(out) == [(0, 1), (0, 2), (1, 2)]
                    elif not _intx_only:
                        assert list(out) == \
                            [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
                elif _max_degree == 3:
                    if _intx_only:
                        assert list(out) == [(0, 1), (0, 2), (1, 2), (0, 1, 2)]
                    elif not _intx_only:
                        assert list(out) == \
                           [
                               (0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2),
                               (0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 1),
                               (0, 1, 2), (0, 2, 2), (1, 1, 1), (1, 1, 2),
                               (1, 2, 2), (2, 2, 2)
                           ]
                else:
                    raise Exception

            else:
                raise Exception

        else:
            raise Exception











