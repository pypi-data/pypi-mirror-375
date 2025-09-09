# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



import pytest

import re

import sklearn

from sklearn.utils.estimator_checks import (
    check_transformer_general,
    check_transformers_unfitted,
    check_transformer_preserve_dtypes,
    check_transformer_get_feature_names_out,
    check_transformer_get_feature_names_out_pandas
)

from pybear.preprocessing import SlimPolyFeatures as SlimPoly



class TestSKLearnCheckTransformer:


    sk_version = sklearn.__version__


    def test_transformers_unfitted(self):
        # this tests if Exception raised when transform() without fit()
        check_transformers_unfitted(
            'SlimPoly',
            SlimPoly()
        )


    def test_transformer_general(self):

        check_transformer_general(
            'SlimPoly',
            SlimPoly()
        )


    def test_transformer_preserve_dtypes(self):
        check_transformer_preserve_dtypes(
            'SlimPoly',
            SlimPoly()
        )


    def test_check_transformer_get_feature_names_out(self):
        # looks for certain verbiage in error if len(input_features) does not
        # match n_features_in_, and checks if output dtype is object

        if float(self.sk_version[0:3]) >= 1.6:
            check_transformer_get_feature_names_out(
                'SlimPoly',
                SlimPoly()
            )
        else:
            err_msg = f"'SlimPolyFeatures' object has no attribute '_get_tags'"
            with pytest.raises(AttributeError, match=re.escape(err_msg)):
                check_transformer_get_feature_names_out(
                    'SlimPoly',
                    SlimPoly()
                )


    def test_check_transformer_get_feature_names_out_pandas(self):
        # looks for certain verbiage in error if 'input_features' does not
        # match feature_names_in_ if was fit on a dataframe

        if float(self.sk_version[0:3]) >= 1.6:
            check_transformer_get_feature_names_out_pandas(
                'SlimPoly',
                SlimPoly()
            )
        else:
            err_msg = f"'SlimPolyFeatures' object has no attribute '_get_tags'"
            with pytest.raises(AttributeError, match=re.escape(err_msg)):
                check_transformer_get_feature_names_out_pandas(
                    'SlimPoly',
                    SlimPoly()
                )





