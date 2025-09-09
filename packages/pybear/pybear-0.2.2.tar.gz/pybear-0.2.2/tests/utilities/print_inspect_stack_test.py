# Authors:
#
#       Bill Sousa
#
# License: BSD 3 clause



import pytest
from pybear.utilities._print_inspect_stack import print_inspect_stack as pis
import inspect


@pytest.mark.parametrize('a',
    (True, None, 0, 1, 3.14, [], {'a':1}, {}, (), 'junk', ['more', 'junk'])
)
def test_rejects_non_callables(a):
    with pytest.raises(TypeError):
        pis(a)


class TestRejectsCallablesThatAreNotInpectStack:


    def test_rejects_non_callable1(self):
        def junk_function():
            return f'some trash'

        with pytest.raises(TypeError):
            pis(junk_function)


    def test_rejects_non_callable2(self):

        junk_lambda = lambda: f'some garbage'

        with pytest.raises(TypeError):
            pis(junk_lambda)



def test_accepts_inspect_stack():
    pis(inspect.stack)










