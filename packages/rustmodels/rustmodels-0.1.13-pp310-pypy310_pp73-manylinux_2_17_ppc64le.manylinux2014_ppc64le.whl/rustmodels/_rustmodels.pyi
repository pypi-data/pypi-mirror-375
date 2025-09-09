import polars as pl
from enum import Enum

########## Formula Utils ##########

class FormulaTerm:
    """
    A class representing a single term in a formula.

    Used in a Formula object. 

    Attributes:
        name (str): The name of the term as it appears in the formula (e.g., "x1", "x2", "x1:x2").
        subtracted (bool): True if the term is being removed from the formula (i.e., "- x2").
        intercept (bool): True if the term is an intercept term (i.e., "1" in the formula).
        interaction (bool): True if this is an interaction term (e.g., "x1:x2").
    """
    @property
    def name(self) -> str:
        """The name of the term as it appears in the formula (e.g., "x1", "x2", "x1:x2")."""
    @property
    def subtracted(self) -> bool:
        """True if the term is being removed from the formula (i.e., "- x2")."""
    @property
    def intercept(self) -> bool: 
        """True if the term is an intercept term (i.e., "1" in the formula)."""
    @property
    def interaction(self) -> bool: 
        """True if this is an interaction term (e.g., "x1:x2")."""
    
    def get_columns_from_term(self) -> list[str]:
        """A method to find all columns used to create this term."""

class Formula:
    """
    An object used to represent a model formula.

    Attributes:
        original (str): The original formula string as provided by the user.
        dependent (FormulaTerm): The dependent variable term.
        independent (List[FormulaTerm]): A list of independent variable terms.
    """
    @property
    def original(self) -> str:
        """The original formula string as provided by the user."""
    @property
    def dependent(self) -> FormulaTerm:
        """The dependent variable term."""
    @property
    def independent(self) -> list[FormulaTerm]:
        """A list of independent variable terms."""

    def get_column_names(self, with_dependent: bool = True) -> list[str]:
        """
        Finds the name of every column in a formula.

        Args:
            with_dependent (bool): A boolean that if true indicates we would like for 
                the dependent variable column name to be added in to the returned list.
        """

def _parse_formula(formula: str) -> Formula:
    """
    An internal function to take in a user-defined string and return a Formula object.

    Args:
        formula (str): A string representing the formula, using R-style syntax (e.g., "y ~ x1 + x2 - x3").

    Returns:
        Formula: A Formula object representing the parsed formula.
    """

def _is_numeric(s: str) -> bool: ...

########## Model Matrix Utils ##########

class EncodingType(Enum):
    """
    An enum representing the type of encoding used for variables.

    Attributes:
        Dummy: Dummy encoding
        OneHot: One-hot encoding
        Cast: Direct cast for boolean variables
        Same: Variables that don't need transformation at all
    """
    Dummy: ...
    OneHot: ...
    Cast: ...
    Same: ...

    @property
    def name(self) -> str:
        """The name of the enum variant."""

class EncodedColumnInfo:
    """
    A class representing information about how a column is encoded.

    Attributes:
        levels (List[str] | None): All levels for categorical variables. Reference level should be the first (index 0).
        encoding_type (EncodingType): The type of encoding used for the variable.
    """
    def __init__(self, levels: list[str] | None, encoding_type: EncodingType) -> None: ...

    @property
    def levels(self) -> list[str] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""
    @property
    def encoding_type(self) -> EncodingType:
        """The type of encoding used for the variable."""

class Encoder:
    """
    A class to handle encoding of variables in a model matrix.

    Attributes:
        column_mappings (Dict[str, EncodedColumnInfo]): A mapping of column name to info on the encoding.
    """
    def __init__(self) -> None: ...    

    @property
    def column_mappings(self) -> dict[str, EncodedColumnInfo]:
        """A mapping of column name to info on the encoding."""
    
    @column_mappings.setter
    def column_mappings(self, value: dict[str, EncodedColumnInfo]) -> None: ...

    def add_column_mapping(self, col_name: str, col_info: EncodedColumnInfo) -> None:
        """
        Adds a single column and its encoding info to the mapping.
        """

    def get_column_mapping(self, col_name: str) -> EncodedColumnInfo | None:
        """
        Gets the encoding info for a single column.

        Args:
            col_name (String): The name of the column to retrieve.

        Returns:
            EncodedColumnInfo | None: The encoding information for the column,
                or None if the column is not found in the mapping.
        """

########## LinReg ##########

def fit_linear_regression(formula: str, data: pl.DataFrame) -> object: ...
