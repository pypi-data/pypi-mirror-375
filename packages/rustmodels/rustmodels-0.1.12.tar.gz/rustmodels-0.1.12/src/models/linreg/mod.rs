use pyo3::prelude::*;

// use pyo3::prelude::*;
// use pyo3_arrow::PyArrowType;
// use arrow::record_batch::RecordBatch;
// use arrow::array::*;
// use arrow::datatypes::*;
// use std::sync::Arc;

use pyo3_arrow::PyTable;

// ---------- Import submodules ----------

// use crate::models::utils::model_matrix_utils;

use super::utils::formula_utils;

// ---------- Linreg module functions ----------

// REMEMBER: If possible, use GPU for speed

/// Function that fits and returns a linear regression.
///
/// Args:
/// - `formula` (string): Formula for the regression taking place. This will use the R formula syntax, and will use a 'formula' object.
/// - `data` (python dictionary): A dictionary containing the data to fit the model. It will be used in conjunction with the formula.
///     It will have column names as keys and column values as values in lists.
///
/// Returns:
/// - A 'linreg' object.
#[pyfunction]
pub fn fit_linear_regression(formula: &str, _data: PyTable) -> PyResult<String> {
    // We need to remember that eventually, pass down a struct of type LinReg or something, where
    // it will record info about the model as it is created(like encoding info for categorical data), 
    // then return that struct.

    // Update: Pass Encoder struct through get_model_matrix and then put the encoder into the 
    //  model struct at the end of this function before returning


    // Steps:
    // 1. Parse the formula to identify dependent and independent variables.  - Use _parse_formula
    let _formula: formula_utils::Formula = formula_utils::parse_formula(formula)?;

    // 2. Extract the relevant columns from the DataFrame and create the model matrices.                - Use _get_model_matrix
    // let _model_matrix: String = model_matrix_utils::get_model_matrix(&formula, _data)?;
    // println!("{:#?}", model_matrix);

    // 3. Perform the linear regression using matrix operations.                                        - Use _linear_regression
    // 4. Return the results as a 'linreg' object.                                                      - Use _create_linreg_result_object
    Ok("LinReg placeholder string!".to_string())
}

/// Internal function to create the linreg submodule. Should be run in src/lib.rs.
pub fn _create_linreg_module(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "linreg")?;
    m.add_function(wrap_pyfunction!(fit_linear_regression, &m)?)?;
    Ok(m)
}

// ---------- Linreg module struct ----------

// struct linreg {

// }


