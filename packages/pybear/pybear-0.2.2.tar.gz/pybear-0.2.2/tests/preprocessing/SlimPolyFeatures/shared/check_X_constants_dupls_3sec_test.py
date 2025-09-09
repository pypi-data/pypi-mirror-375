# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from pybear.preprocessing._SlimPolyFeatures._shared._check_X_constants_dupls \
    import _check_X_constants_dupls



class TestCheckXConstantsDupls:


    @pytest.mark.parametrize('_X_constants',
        (
            -2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0,1], (0,1),
            {0,1}, {'a':1}, lambda x: x
         )
    )
    def test_X_constants_rejects_junk(self, _X_constants):

        with pytest.raises(AssertionError):
            _check_X_constants_dupls(_X_constants, [])


    @pytest.mark.parametrize('_X_constants', ({}, {1: 1}))
    def test_X_constants_only_accepts_good_dict(self, _X_constants):

        if not len(_X_constants):
            # raises for bad type
            _check_X_constants_dupls(_X_constants, [])
        else:
            # raises for other reason, having constants
            with pytest.raises(ValueError):
                _check_X_constants_dupls(_X_constants, [])


    @pytest.mark.parametrize('_X_dupls',
        (
            -2.7, -1, 0, 1, 2.7, True, False, None, 'junk', [0, 1], (0, 1),
            {0, 1}, {'a': 1}, lambda x: x
        )
    )
    def test_X_dupls_rejects_junk(self, _X_dupls):

        with pytest.raises(AssertionError):
            _check_X_constants_dupls({}, _X_dupls)


    @pytest.mark.parametrize('_X_dupls', ([], [[0,1]], [[0,1],[2,3]]))
    def test_X_dupls_accepts_good_list(self, _X_dupls):

        if not len(_X_dupls):
            # raises for bad type
            _check_X_constants_dupls({}, _X_dupls)
        else:
            # raises for other reason, having constants
            with pytest.raises(ValueError):
                _check_X_constants_dupls({}, _X_dupls)


    def test_rejects_X_has_constants_and_dupls(self):

        with pytest.raises(ValueError):
            _check_X_constants_dupls(
                {0:0, 1:1, 2:2},
                [[3,4], [5,6]]
            )


    def test_rejects_X_has_constants(self):

        with pytest.raises(ValueError):
            _check_X_constants_dupls(
                {0:0, 1:1, 2:2},
                []
            )


    def test_rejects_X_has_dupls(self):

        with pytest.raises(ValueError):
            _check_X_constants_dupls(
                {},
                [[3,4], [5,6]]
            )


    def test_accepts_no_constants_no_dupls(self):

            assert _check_X_constants_dupls({}, []) is None











