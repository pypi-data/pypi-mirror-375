# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



from pybear.preprocessing._SlimPolyFeatures._get_feature_names_out. \
    _gfno_poly import _gfno_poly

import numpy as np

import pytest



class TestGFNOPoly:


    # def _gfno_poly(
    #     _X_feature_names_in: npt.NDArray[object],
    #     _active_combos: tuple[tuple[int, ...], ...],
    #     _feature_name_combiner: FeatureNameCombinerType
    # ) -> npt.NDArray[object]:

    # _feature_name_combiner: (
    #     Callable[[Sequence[str], tuple[tuple[int, ...], ...]], str],
    #     | Literal['as_feature_names', 'as_indices']
    # )

    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    # this is not exhaustive! merely shows that some catching is working.
    # by right, all the validation in the module could be removed.

    JUNK = (-2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0, 1],
            (0, 1), {'a': 1}, lambda x, y: f"{x}&{y}")


    @pytest.mark.parametrize('junk_feature_names_in_', JUNK)
    def test_feature_names_in_rejects_junk(self, junk_feature_names_in_):

        with pytest.raises(AssertionError):

            _gfno_poly(
                junk_feature_names_in_,
                _active_combos=((0,0), (0,1), (1,1)),
                _feature_name_combiner='as_indices'
            )


    @pytest.mark.parametrize('junk_active_combos', JUNK)
    def test_active_combos_rejects_junk(self, junk_active_combos):

        with pytest.raises(AssertionError):

            _gfno_poly(
                _X_feature_names_in=np.array(['a', 'b'], dtype=object),
                _active_combos=junk_active_combos,
                _feature_name_combiner='as_indices'
            )


    @pytest.mark.parametrize('junk_feature_name_combiner', JUNK)
    def test_feature_name_combiner_rejects_junk(self, junk_feature_name_combiner):

        if callable(junk_feature_name_combiner):
            _gfno_poly(
                _X_feature_names_in=np.array(['a', 'b'], dtype=object),
                _active_combos=((0, 0), (0, 1), (1, 1)),
                _feature_name_combiner=junk_feature_name_combiner
            )

        else:
            with pytest.raises(AssertionError):

                _gfno_poly(
                    _X_feature_names_in=np.array(['a', 'b'], dtype=object),
                    _active_combos=((0,0), (0,1), (1,1)),
                    _feature_name_combiner=junk_feature_name_combiner
                )

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    @pytest.mark.parametrize('_active_combos',
        (((0, 0), (0, 1), (1, 1)), ((0, 1), (1, 1)), ((1, 1),))
    )
    def test_accuracy_as_indices(self, _active_combos):

        _feature_names_in = np.array(['a', 'b'], dtype=object)

        out = _gfno_poly(
            _X_feature_names_in=_feature_names_in,
            _active_combos=_active_combos,
            _feature_name_combiner='as_indices'
        )

        assert isinstance(out, np.ndarray)
        assert out.dtype == object
        assert np.array_equal(out, list(map(str, _active_combos)))



    @pytest.mark.parametrize('_active_combos',
        (((0, 0), (0, 1), (1, 1)), ((0, 1), (1, 1)), ((1, 1),))
    )
    def test_accuracy_as_feature_names(self, _active_combos):

        _feature_names_in = np.array(['a', 'b'], dtype=object)

        out = _gfno_poly(
            _X_feature_names_in=_feature_names_in,
            _active_combos=_active_combos,
            _feature_name_combiner='as_feature_names'
        )

        assert isinstance(out, np.ndarray)
        assert out.dtype == object

        if _active_combos == ((0, 0), (0, 1), (1, 1)):
            assert np.array_equal(out, ['a^2', 'a_b', 'b^2'])
        elif _active_combos == ((0, 1), (1, 1)):
            assert np.array_equal(out, ['a_b', 'b^2'])
        elif _active_combos == ((1, 1),):
            assert np.array_equal(out, ['b^2'])
        else:
            raise Exception


    @pytest.mark.parametrize('_callable_trial', ('callable1', 'callable2'))
    @pytest.mark.parametrize('_active_combos',
        (((0, 0), (0, 1), (1, 1)), ((0, 1), (1, 1)), ((1, 1), ))
    )
    def test_accuracy_as_callable(self, _callable_trial, _active_combos):

        _feature_names_in = np.array(['a', 'b'], dtype=object)

        if _callable_trial == 'callable1':
            _feature_name_combiner = \
                lambda feature_names, combos: '+'.join(map(str, combos))
        elif _callable_trial == 'callable2':
            # this deliberately creates duplicate feature names to force raise
            _feature_name_combiner = lambda feature_names, combos: feature_names[0]
        else:
            raise Exception()

        if _callable_trial == 'callable2':
            with pytest.raises(ValueError):
                _gfno_poly(
                    _X_feature_names_in=_feature_names_in,
                    _active_combos=_active_combos,
                    _feature_name_combiner=_feature_name_combiner
                )
        else:

            out = _gfno_poly(
                _X_feature_names_in=_feature_names_in,
                _active_combos=_active_combos,
                _feature_name_combiner=_feature_name_combiner
            )

            assert isinstance(out, np.ndarray)
            assert out.dtype == object

            # lambda feature_names, combos: '+'.join(map(str, combos))
            if _active_combos == ((0, 0), (0, 1), (1, 1)):
                assert np.array_equal(out, ['0+0', '0+1', '1+1'])
            elif _active_combos == ((0, 1), (1, 1)):
                assert np.array_equal(out, ['0+1', '1+1'])
            elif _active_combos == ((1, 1),):
                assert np.array_equal(out, ['1+1'])
            else:
                raise Exception










