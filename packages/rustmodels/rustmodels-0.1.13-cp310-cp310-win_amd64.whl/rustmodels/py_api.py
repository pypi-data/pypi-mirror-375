from . import _rustmodels as rm, _model_matrix as mm, _linreg as linreg
import polars as pl
from pydantic import validate_call, ConfigDict

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def fit_linear_regression(formula: str, df: pl.DataFrame) -> linreg.LinearRegression:
    """
    Function that performs a linear regression fit.

    Args:
        formula (str): Formula for the regression taking place. This will use the R formula syntax.
        df (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used in 
            conjunction with the formula to create the model matrix. 

    Returns:
        LinearRegression: A 'LinearRegression' object containing the regression results.
    """
    # Parse formula in rust
    parsed_formula = rm._parse_formula(formula) # pyright: ignore[reportPrivateUsage]

    # Model matrix in python
    model_matrix = mm.get_model_matrix(df, parsed_formula)
    
    # Matrix math
    linreg_results = linreg.LinearRegression()
    linreg_results.fit(model_matrix)
    
    return linreg_results

