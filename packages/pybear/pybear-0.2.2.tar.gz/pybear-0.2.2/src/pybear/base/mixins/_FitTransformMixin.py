# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



class FitTransformMixin:
    """Provides the `fit_transform` method to pybear transformers."""


    def fit_transform(self, X, y=None, **fit_params):
        """Fit to data, then transform it.

        Fits transformer to `X` and `y` with optional parameters
        `fit_params` and returns a transformed version of `X`.

        Parameters
        ----------
        X : array_like of shape (n_samples, n_features)
            Required. The data.

        y : array_like of shape (n_samples, n_outputs) or (n_samples,)
            Optional, default=None.  Target values (None for unsupervised
            transformations).

        **fit_params : dict
            Additional fit parameters.

        Returns
        -------
        X_tr : array_like of shape (n_samples, n_features_new)
            Transformed array.

        """


        if y is None:
            # fit method of arity 1 (unsupervised transformation)
            X_tr = self.fit(X, **fit_params).transform(X)
        else:
            # fit method of arity 2 (supervised transformation)
            X_tr = self.fit(X, y, **fit_params).transform(X)


        return X_tr






