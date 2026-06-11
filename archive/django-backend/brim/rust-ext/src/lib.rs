use brim_veracity::{user::User, Role};
use pyo3::prelude::*;

#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn create_user(username: String, password: String) -> PyResult<String> {
    let user = User::new(username, password, Role::User);
    serde_json::to_string(&user)
        .map_err(|error| pyo3::exceptions::PyValueError::new_err(error.to_string()))
}

#[pymodule]
fn rust_ext(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(create_user, m)?)?;
    Ok(())
}
