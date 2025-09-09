from ._model_matrix import ModelMatrix
from . import _rustmodels as rm
import numpy as np
import polars as pl
import json

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
        load_from_file(filepath: str): A method that will load a LinearRegression object from a JSON file.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame
        fit(design_matrix: ModelMatrix): Fits the regression model.
    """

    def __init__(self):
        pass

    ########## Public Methods ##########

    def fit(self, design_matrix: ModelMatrix) -> None:
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

    def predict(self, data: pl.DataFrame):
        """
        A method that takes a polars DataFrame and uses it to generate predictions for each 
        row in that DataFrame. The DataFrame must hold data that can be run through this model.
        """
        pass

    def save_to_file(self, filepath: str) -> None:
        """
        A method that will save a LinearRegression object to a JSON file. This file will then
        be available to be loaded and reused.

        Args:
            filepath: The filepath for the saved file

        Returns:
            None
        """
        if not hasattr(self, 'coefficients') or not hasattr(self, '_encoding_data'):
            raise RuntimeError("Model has not been fitted yet. Cannot save an empty model.")

        encoder_data = {}
        for col_name, col_info in self._encoding_data.column_mappings.items():
            encoder_data[col_name] = {
                'levels': col_info.levels,
                'encoding_type': col_info.encoding_type.name
            }

        model_data = {
            'coefficients': self.coefficients,
            'encoder_data': encoder_data
        }

        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=4)

        return None

    def load_from_file(self, filepath: str) -> None:
        """
        A method that will load a LinearRegression object from a JSON file.

        Args:
            filepath: The filepath for the saved file

        Returns:
            None
        """
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        self.coefficients = model_data['coefficients']

        reconstructed_encoder = rm.Encoder()
        for col_name, col_info_data in model_data['encoder_data'].items():
            encoding_type_enum = getattr(rm.EncodingType, col_info_data['encoding_type'])
            reconstructed_col_info = rm.EncodedColumnInfo(
                levels=col_info_data['levels'],
                encoding_type=encoding_type_enum
            )
            reconstructed_encoder.add_column_mapping(col_name, reconstructed_col_info)

        self._encoding_data = reconstructed_encoder
        return

#################### Related functions ####################

def load_linreg(filepath: str) -> LinearRegression:
    """
    A function to load a LinearRegression object from a specified file.

    Args:
        filepath (str): The path to the JSON with a saved LinearRegression object.

    Returns:
        LinearRegression: The loaded object.
    """
    linreg_instance = LinearRegression()
    linreg_instance.load_from_file(filepath)

    return linreg_instance
