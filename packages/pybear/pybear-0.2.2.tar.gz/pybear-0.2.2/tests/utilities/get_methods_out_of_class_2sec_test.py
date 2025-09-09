# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause


import pytest
from pybear.utilities._get_methods_out_of_class import \
    get_methods_out_of_class as gmooc


@pytest.fixture
def good_class():

    class MyClass:
        def __init__(self):
            self.a = None

        def _helper_method(self):
            return None

        def fit(self, anything):
            self.a = 'junk'

        def transform(self, anything):
            return self.a

    return MyClass

@pytest.fixture
def method_names():
    return ['__init__', '_helper_method', 'fit', 'transform']





@pytest.mark.parametrize(
    'not_a_class',
     (0, 1, 3.14, True, False, None, (), [], {}, (1,2), [1,2], {1,2},
      {'a': 1}, lambda: 0, 'junk', ''
     )
)
def test_rejects_everything(not_a_class):
    with pytest.raises(TypeError):
        gmooc(not_a_class)



class TestAcceptsAClass:

    def test_accepts_class(self, good_class):
        gmooc(good_class)


    def test_rejects_class_instance(self, good_class):
        with pytest.raises(TypeError):
            gmooc(good_class())


    def test_returns_list(self, good_class):
        out = gmooc(good_class)
        assert isinstance(out, list)


    def test_returns_all_methods(self, good_class, method_names):
        out = gmooc(good_class)
        for _ in out:
            assert _ in method_names

























