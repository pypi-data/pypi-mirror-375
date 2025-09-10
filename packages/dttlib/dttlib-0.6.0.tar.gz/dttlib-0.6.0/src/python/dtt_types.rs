//! DTT data types needed to process DTT inputs and create DTT outputs
//! On user Python code run from Rust.

use pyo3::{
    pymodule,
    Bound,
    PyResult,
    types::{
        PyModule,
        PyModuleMethods
    }
};
use crate::analysis::types::frequency_domain_array::PyFreqDomainArray;
use crate::analysis::types::time_domain_array::PyTimeDomainArray;
use crate::analysis::result::analysis_id::AnalysisID;

#[cfg(feature = "python-pipe")]
use crate::errors::DTTError;
use crate::params::channel_params::Unit;

#[pymodule]
pub (crate) fn dtt_types(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<AnalysisID>()?;
    m.add_class::<PyFreqDomainArray>()?;
    m.add_class::<PyTimeDomainArray>()?;
    m.add_class::<Unit>()?;
    Ok(())
}

#[cfg(feature = "python-pipe")]
pub (crate) fn dtt_types_init() -> Result<(), DTTError> {
    #[cfg(not(feature = "python"))]
    pyo3::append_to_inittab!(dtt_types);
    Ok(())
}