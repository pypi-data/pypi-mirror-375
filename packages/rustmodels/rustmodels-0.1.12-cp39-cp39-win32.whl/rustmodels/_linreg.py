from ._model_matrix import ModelMatrix
import numpy as np
import polars as pl

#################### Classes ####################

class LinearRegression:
    """
    A class meant to hold the results and metadata of a linear regression.

    Attributes:
        coefficients (dict[str, float]): A dictionary of coefficient names and values.

        _encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
            than the one used to fit. 

    Methods:
        save_to_file(filepath: str): Saves the model to a given filepath.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame

        _fit(design_matrix: ModelMatrix): Fits the regression model.
    """

    def __init__(self, design_matrix: ModelMatrix):
        self._fit(design_matrix)

    def _fit(self, design_matrix: ModelMatrix) -> None:
        """
        A method to fit a linear regression using a ModelMatrix object. Internally saves 
        results and metadata. 
        """
        # Get matrix of results
        X = design_matrix.x_matrix.astype(np.float64)
        Y = design_matrix.y_matrix.astype(np.float64)

        xtx = X.T @ X # X transpose times X
        xty = X.T @ Y # X transpose times Y

        xtxi = np.linalg.inv(xtx)

        results_mat = xtxi @ xty

        # Format results
        results_list: list[float] = [item[0] for item in results_mat.tolist()]
        results_dict = dict(zip(design_matrix.x_col_names, results_list))

        self.coefficients = results_dict
        self._encoding_data = design_matrix.encoding_data # Do this after success of fit

    ########## Public Methods ##########

    def predict(self, data: pl.DataFrame):
        """
        A method that takes a polars DataFrame and uses it to generate predictions for each 
        row in that DataFrame. The DataFrame must hold data that can be run through this model.
        """
        pass

    def save_to_file(self, filepath: str):
        """
        A method that will save a LinearRegression object to a file. This file will then 
        be available to be loaded and reused. 

        Args:
            filepath: The filepath for the saved file

        Returns:
            None
        """
        pass

#################### Related functions ####################

# def load_linreg(filepath: str) -> LinearRegression:
#     """
#     """
#     pass
