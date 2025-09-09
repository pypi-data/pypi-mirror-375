import rustmodels

import pytest
import polars as pl
from pydantic import ValidationError

@pytest.mark.parametrize("formula_str, df", [
    (5, pl.DataFrame({"x1": [1, 2], "x2": [3, 4]})),
    ("y ~ x1 + x2", "not_a_dataframe"),
])
def test_linreg_type_errors(
    formula_str,
    df
):
    """
    Test where the linear regression function should raise validation errors.
    """
    with pytest.raises(ValidationError):
        rustmodels.fit_linear_regression(formula_str, df)



