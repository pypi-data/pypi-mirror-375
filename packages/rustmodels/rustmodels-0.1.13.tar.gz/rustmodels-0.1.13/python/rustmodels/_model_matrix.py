import polars as pl
from ._rustmodels import Formula, Encoder, EncodedColumnInfo, EncodingType
import numpy as np
from typing import Tuple
from dataclasses import dataclass

#################### Classes ####################

@dataclass
class ModelMatrix:
    """
    A class meant to hold the model matrices as well as Encoding metadata

    Attributes:
        x_matrix (numpy.ndarray): A matrix meant to represent the independent variable
        y_matrix (numpy.ndarray): A matrix meant to represent the dependent variable
        x_col_names (list[str]): The column names for the x_matrix
        encoding_data (Encoder): A collection of metadata on how the data was encoded
    """
    x_matrix: np.ndarray
    y_matrix: np.ndarray
    x_col_names: list[str]
    encoding_data: Encoder

#################### Main function ####################

def get_model_matrix(data: pl.DataFrame, formula: Formula) -> ModelMatrix:
    """
    A function meant to create model matrices from a DataFrame and a formula.

    Cleans the DataFrame and formats the matrices.

    Args:
        data (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used 
            in conjunction with the formula to create the model matrix.
        formula (Formula): A Formula object representing the model formula.

    Returns:
        ModelMatrix: A ModelMatrix object holding final matrices and encoding info
    """
    ##### Plan #####
    # Copy how I did it in rust

    # 1) Validate
    # 2) Select relevant columns and then filter
    # 3) Encode and save encoding metadata to Encoder class for future

    # Format the dataframe as we want it
        # Make each relevant column into a matrix
        # Format x and y matrices from that

    # Turn into matrix

    ##### Functionality #####
    _ = validate_data_and_formula(data, formula)
    data = select_and_filter(data, formula)
    model_matrices = make_into_matrices(data, formula)
    return model_matrices

#################### Helper functions ####################

def make_into_matrices(data: pl.DataFrame, formula: Formula) -> ModelMatrix:
    """
    A function meant to create model matrices from a cleaned DataFrame and a formula.

    Args:
        data (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used 
            in conjunction with the formula to create the model matrix.
        formula (Formula): A Formula object representing the model formula.

    Returns:
        ModelMatrix: A ModelMatrix object holding final matrices and encoding info
    """
    encoder = fit_encoder(data, formula)
    x_matrix, y_matrix, x_col_names = encode_data(data, formula, encoder)
    model_matrix = ModelMatrix(x_matrix, y_matrix, x_col_names, encoder)

    return model_matrix

def encode_data(data: pl.DataFrame, formula: Formula, encoder: Encoder) -> Tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Turns the data into matrices for X and Y respectively. Used after the data has 
    already been fit for encoding.
    """
    # Y matrix
    y_col = formula.dependent.name
    dep_encoding = encoder.get_column_mapping(y_col)
    if dep_encoding is None:
        raise EncodingError(f"Dependent variable {y_col} not found in encodings")
    
    encoding_type = dep_encoding.encoding_type
    if encoding_type not in [EncodingType.Cast, EncodingType.Same]:
        raise EncodingError(f"Dependent variable {y_col} encoded as {dep_encoding.encoding_type}, not numeric/boolean")
    
    y_matrix = data.select(y_col).to_numpy()

    # X Matrix
    x_cols_expressions: list[pl.Expr] = []

    for term in formula.independent:
        if term.intercept:
            # Add an expression for a column of 1s for the intercept
            x_cols_expressions.append(pl.lit(1, dtype=pl.Int8).alias("intercept"))
            continue
        elif term.interaction:
            interaction_cols = term.get_columns_from_term()
            if len(interaction_cols) != 2:
                raise NotImplementedError("Only 2-way interactions are currently supported.")

            col1_name, col2_name = interaction_cols[0], interaction_cols[1]
            col1_encoding = encoder.get_column_mapping(col1_name)
            col2_encoding = encoder.get_column_mapping(col2_name)

            if col1_encoding is None or col2_encoding is None:
                raise EncodingError(f"Interaction term {term.name} not found in encodings")

            numeric_encodings = [EncodingType.Same, EncodingType.Cast]
            is_col1_numeric = col1_encoding.encoding_type in numeric_encodings
            is_col2_numeric = col2_encoding.encoding_type in numeric_encodings
            is_col1_dummy = col1_encoding.encoding_type == EncodingType.Dummy
            is_col2_dummy = col2_encoding.encoding_type == EncodingType.Dummy

            if is_col1_numeric and is_col2_numeric:
                interaction_expr = (
                    pl.col(col1_name).cast(pl.Float64) * pl.col(col2_name).cast(pl.Float64)
                ).alias(f"{col1_name}:{col2_name}")
                x_cols_expressions.append(interaction_expr)
            elif (is_col1_dummy and is_col2_numeric) or (is_col2_dummy and is_col1_numeric):
                if is_col1_dummy:
                    dummy_col_name, numeric_col_name = col1_name, col2_name
                    dummy_encoding_info = col1_encoding
                else:
                    dummy_col_name, numeric_col_name = col2_name, col1_name
                    dummy_encoding_info = col2_encoding

                levels = dummy_encoding_info.levels
                if levels and len(levels) >= 2:
                    numeric_expr = pl.col(numeric_col_name).cast(pl.Float64)
                    for level in levels[1:]:  # Drop first level
                        dummy_expr = pl.when(pl.col(dummy_col_name) == level).then(1).otherwise(0)
                        interaction_expr = (numeric_expr * dummy_expr).alias(
                            f"{dummy_col_name}_{level}:{numeric_col_name}"
                        )
                        x_cols_expressions.append(interaction_expr)
            elif is_col1_dummy and is_col2_dummy:
                levels1 = col1_encoding.levels
                levels2 = col2_encoding.levels

                if levels1 and len(levels1) >= 2 and levels2 and len(levels2) >= 2:
                    for level1 in levels1[1:]:
                        for level2 in levels2[1:]:
                            dummy1_expr = pl.when(pl.col(col1_name) == level1).then(1).otherwise(0)
                            dummy2_expr = pl.when(pl.col(col2_name) == level2).then(1).otherwise(0)
                            interaction_expr = (dummy1_expr * dummy2_expr).alias(
                                f"{col1_name}_{level1}:{col2_name}_{level2}"
                            )
                            x_cols_expressions.append(interaction_expr)
            else:
                raise NotImplementedError("This interaction type is not yet implemented.")
        else: # Handle simple (non-interaction, non-intercept) terms
            col_name = term.name
            encoding_info = encoder.get_column_mapping(col_name)

            if encoding_info is None:
                raise EncodingError(f"Independent variable {col_name} not found in encodings")
            
            if encoding_info.encoding_type == EncodingType.Dummy:
                levels = encoding_info.levels
                if levels is None:
                    raise EncodingError(f"No levels found for {col_name}")

                # Drop the first level as the reference category, then create a column for all of the rest
                # We can't use to_dummies if we want to evaluate lazily
                for level in levels[1:]:
                    expr = pl.when(pl.col(col_name) == level).then(1).otherwise(0).alias(f"{col_name}_{level}")
                    x_cols_expressions.append(expr)

            elif encoding_info.encoding_type == EncodingType.Cast:
                x_cols_expressions.append(pl.col(col_name).cast(pl.Int8))

            elif encoding_info.encoding_type == EncodingType.Same:
                x_cols_expressions.append(pl.col(col_name))

    if not x_cols_expressions:
        x_matrix = np.empty((data.height, 0))
        x_col_names = []
    else:
        temp_df = data.select(x_cols_expressions)
        x_col_names = temp_df.columns
        x_matrix = temp_df.to_numpy()

    return x_matrix, y_matrix, x_col_names

def fit_encoder(data: pl.DataFrame, formula: Formula) -> Encoder:
    """
    Goes through the data once and finds out how the data will be encoded
    """
    schema = data.schema
    formula_cols = formula.get_column_names()
    encoder = Encoder()

    for col in formula_cols: # Not a try/except block because data has been validated already
        data_type: pl.DataType = schema[col]
        if data_type in [
            # Integer types
            pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Int128,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            # Float types
            pl.Float32, pl.Float64
        ]:
            encoding_info = EncodedColumnInfo(
                None,
                EncodingType.Same
            )
        elif data_type == pl.Boolean:
            encoding_info = EncodedColumnInfo(
                None,
                EncodingType.Cast
            )
        elif data_type == pl.Utf8:
            levels = data[col].unique().to_list()
            _ = levels.sort()
            encoding_info = EncodedColumnInfo(
                levels,
                EncodingType.Dummy
            )
        else:
            raise EncodingError(f"Column {col} has unimplemented data type {str(data_type)}")
            
        encoder.add_column_mapping(col, encoding_info)

    return encoder

def select_and_filter(data: pl.DataFrame, formula: Formula) -> pl.DataFrame:
    """
    A function to select only the 

    Args:
        data (pl.DataFrame): The DataFrame to be edited
        formula (Formula): A formula object that will be used to select the relevant columns
            and filter them

    Returns:
        pl.DataFrame: A polars DataFrame with only relevant data included
    """
    # Select relevant cols
    formula_cols = formula.get_column_names()
    relevant_data = data.select(formula_cols)

    # Filter out nulls
    relevant_data = relevant_data.drop_nulls().drop_nans()

    return relevant_data

def validate_data_and_formula(data: pl.DataFrame, formula: Formula):
    """
    A function to validate that:
        1) The data isn't empty
        2) Each necessary column exists

    Args:
        data (pl.DataFrame): The polars DataFrame being validated
        formula (Formula): The formula being validated

    Returns:
        None

    Raises:
        DataValidationError: If the input DataFrame is empty or if formula columns cannot 
            be found
    """
    # Not empty
    if data.is_empty():
        raise DataValidationError("Empty DataFrame passed: Input must have data")

    # Each column exists
    formula_cols = formula.get_column_names()
    dataframe_cols = data.columns

    for col in formula_cols:
        if col not in dataframe_cols:
            raise DataValidationError(f"Column {col} found in formula but not found in the data")
    
    return

#################### Errors ####################

class DataValidationError(ValueError):
    """
    Error raised when data and formula do not line up
    """
    pass

class EncodingError(ValueError):
    """
    Error raised when the encoding of the data for the Model Matrix goes wrong 
    or has obviously incorrect elements to it.
    """
    pass
