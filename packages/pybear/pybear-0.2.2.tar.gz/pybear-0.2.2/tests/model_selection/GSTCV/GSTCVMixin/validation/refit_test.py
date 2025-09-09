# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

from sklearn.metrics import accuracy_score, balanced_accuracy_score

from pybear.model_selection.GSTCV._GSTCVMixin._validation._refit import \
    _val_refit



class TestValRefit:

    # def _val_refit(
    #     _refit: RefitType,
    #     _scoring: ScorerInputType
    # ) -> None:



    # 'scoring' comes into _val_refit in validated but pre-conditioned
    # state. could be str, callable, list-like, dict.
    one_scorer = {
        'bear_score': lambda x, y: 0.8394239847
    }
    two_scorers = {
        'accuracy': accuracy_score,
        'balanced_accuracy': balanced_accuracy_score
    }


    @pytest.mark.parametrize('n_scorers', (one_scorer, two_scorers))
    @pytest.mark.parametrize('junk_refit',
        (0, 1, 3.14, None, [0,1], (0,1), {0,1}, {'a':1})
    )
    def test_reject_junk_refit(self, n_scorers, junk_refit):
        with pytest.raises(TypeError):
            _val_refit(junk_refit, n_scorers)


    @pytest.mark.parametrize('n_scorers', (one_scorer, two_scorers))
    @pytest.mark.parametrize('_callable',
        (lambda X: 0, lambda X: len(X['params'])-1, lambda X: 'trash')
    )
    def test_accepts_callable(self, n_scorers, _callable):
        assert _val_refit(_callable, n_scorers) is None


    @pytest.mark.parametrize('n_scorers', (one_scorer, two_scorers))
    def test_accepts_False(self, n_scorers):

        if len(n_scorers) == 1:
            assert _val_refit(False, n_scorers) is None

        elif len(n_scorers) == 2:
            with pytest.warns():
                assert _val_refit(False, n_scorers) is None


    @pytest.mark.parametrize('n_scorers', (one_scorer,))
    def test_single_accepts_true(self, n_scorers):
        assert _val_refit(True, n_scorers) is None


    @pytest.mark.parametrize('n_scorers', (two_scorers,))
    def test_multi_rejects_true(self, n_scorers):
        with pytest.raises(ValueError):
            _val_refit(True, n_scorers)


    @pytest.mark.parametrize('n_scorers', (one_scorer, two_scorers))
    @pytest.mark.parametrize('junk_string', ('trash', 'garbage', 'junk'))
    def test_rejects_junk_strings(self, n_scorers, junk_string):
        with pytest.raises(ValueError):
            _val_refit(junk_string, n_scorers)


    @pytest.mark.parametrize('n_scorers', (two_scorers,))
    def test_accepts_good_strings(self, n_scorers):
        if len(n_scorers) == 1:
            assert _val_refit('ACCURACY', n_scorers) is None
        if len(n_scorers) == 2:
            assert _val_refit('BALANCED_ACCURACY', n_scorers) is None






