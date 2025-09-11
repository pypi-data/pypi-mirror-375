use crate::datafusion::context::make_datafusion_context;
use crate::expression::compiler::call::{default_callables, VegaFusionCallable};
use crate::plan_executor::DataFusionPlanExecutor;
use crate::task_graph::timezone::RuntimeTzConfig;
use num_traits::float::FloatConst;
use std::collections::HashMap;
use std::sync::Arc;
use vegafusion_common::datafusion_common::ScalarValue;
use vegafusion_core::data::dataset::VegaFusionDataset;
use vegafusion_core::runtime::PlanExecutor;

#[derive(Clone)]
pub struct CompilationConfig {
    pub signal_scope: HashMap<String, ScalarValue>,
    pub data_scope: HashMap<String, VegaFusionDataset>,
    pub callable_scope: HashMap<String, VegaFusionCallable>,
    pub constants: HashMap<String, ScalarValue>,
    pub tz_config: Option<RuntimeTzConfig>,
    pub plan_executor: Arc<dyn PlanExecutor>,
}

impl Default for CompilationConfig {
    fn default() -> Self {
        let ctx = Arc::new(make_datafusion_context());
        let plan_executor = Arc::new(DataFusionPlanExecutor::new(ctx)) as Arc<dyn PlanExecutor>;

        Self {
            signal_scope: Default::default(),
            data_scope: Default::default(),
            callable_scope: default_callables(),
            constants: default_constants(),
            tz_config: None,
            plan_executor,
        }
    }
}

/// ## Constants
/// Constant values that can be referenced by name within expressions.
///
/// See: https://vega.github.io/vega/docs/expressions/#bound-variables
fn default_constants() -> HashMap<String, ScalarValue> {
    let mut constants = HashMap::new();

    // # NaN
    // Not a number. Same as the JavaScript literal NaN.
    constants.insert("NaN".to_string(), ScalarValue::from(f64::NAN));

    // # E
    // The transcendental number e. Same as JavaScript’s Math.E.
    constants.insert("E".to_string(), ScalarValue::from(f64::E()));

    // # LN2
    // The natural log of 2. Same as JavaScript’s Math.LN2.
    constants.insert("LN2".to_string(), ScalarValue::from(f64::LN_2()));

    // # LN10
    // The natural log of 10. Same as JavaScript’s Math.LN10.
    constants.insert("LN10".to_string(), ScalarValue::from(f64::LN_10()));

    // # LOG2E
    // The base 2 logarithm of e. Same as JavaScript’s Math.LOG2E.
    constants.insert("LOG2E".to_string(), ScalarValue::from(f64::LOG2_E()));

    // # LOG10E
    // The base 10 logarithm e. Same as JavaScript’s Math.LOG10E.
    constants.insert("LOG10E".to_string(), ScalarValue::from(f64::LOG10_E()));

    // # MAX_VALUE
    // The largest positive numeric value. Same as JavaScript’s Number.MAX_VALUE.
    constants.insert("MAX_VALUE".to_string(), ScalarValue::from(f64::MAX));

    // # MIN_VALUE
    // The smallest positive numeric value. Same as JavaScript’s Number.MIN_VALUE.
    constants.insert(
        "MIN_VALUE".to_string(),
        ScalarValue::from(f64::MIN_POSITIVE),
    );

    // # PI
    // The transcendental number π. Same as JavaScript’s Math.PI.
    constants.insert("PI".to_string(), ScalarValue::from(f64::PI()));

    // # SQRT1_2
    // The square root of 0.5. Same as JavaScript’s Math.SQRT1_2.
    constants.insert(
        "SQRT1_2".to_string(),
        ScalarValue::from(f64::FRAC_1_SQRT_2()),
    );

    // # SQRT2
    // The square root of 2. Same as JavaScript’s Math.SQRT2.
    constants.insert("SQRT2".to_string(), ScalarValue::from(f64::SQRT_2()));

    constants
}
