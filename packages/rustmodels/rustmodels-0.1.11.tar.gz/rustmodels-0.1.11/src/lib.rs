// ---------- Imports  ----------
// Library imports
use pyo3::prelude::*;

mod models;
// use crate::models;
// use pyo3::create_exception;
// use ndarray::prelude::*;

// Declare submodules
// mod models;

// use models::utils::formula_utils::FormulaError as RustFormulaError;


// ---------- Make main module  ----------

/// A Python module for simpler statistical modeling implemented in Rust. 
/// Much of the code is modeled after R's syntax for specifying models. 
/// Includes:
/// 
/// - Linear regression: Modeled after R's lm() function
#[pymodule]
#[pyo3(name = "_rustmodels")]
fn rustmodels(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add all functions to the main module. A flat implementation is 
    // easier for users

    // ----- Linreg -----
    m.add_function(wrap_pyfunction!(models::linreg::fit_linear_regression, m)?)?;

    // All errors

    // m.add("FormulaError", _py.get_type::<FormulaError>())?;

    // ----- Classes -----
    m.add_class::<models::utils::formula_utils::Formula>()?;
    m.add_class::<models::utils::formula_utils::FormulaTerm>()?;
    m.add_class::<models::utils::model_matrix_utils::Encoder>()?;
    m.add_class::<models::utils::model_matrix_utils::EncodedColumnInfo>()?;
    m.add_class::<models::utils::model_matrix_utils::EncodingType>()?;

    // ----- Utils/helper functions -----
    // These will be added here to help with testing. Because they
    // can't be tested in rust, we need to test them in Python.
    m.add_function(wrap_pyfunction!(models::utils::formula_utils::parse_formula, m)?)?;
    m.add_function(wrap_pyfunction!(models::utils::general_utils::is_numeric, m)?)?;
    

    Ok(())
}

// ---------- Errors  ----------

// create_exception!(rustmodels, RustFormulaError, pyo3::exceptions::PyException);
