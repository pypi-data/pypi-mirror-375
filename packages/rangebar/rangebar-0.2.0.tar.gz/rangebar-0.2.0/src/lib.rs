//! Range Bar Construction Library
//! 
//! High-performance, non-lookahead bias range bar construction from Binance UM Futures aggTrades data.
//! 
//! ## Algorithm Overview
//! 
//! Range bars close when price moves ±0.8% from the bar's OPEN price. This ensures:
//! - No lookahead bias: thresholds computed from bar open only
//! - Deterministic results: same input always produces same output
//! - High performance: fixed-point arithmetic with zero-copy data transfer
//! 
//! ## Example Usage
//! 
//! ```python
//! import rangebar_rust
//! import numpy as np
//! 
//! # Fixed-point prices (scaled by 1e8)
//! prices = np.array([5000000000000, 5010000000000, 5040000000000], dtype=np.int64)
//! timestamps = np.array([1000, 2000, 3000], dtype=np.int64)
//! volumes = np.array([100000000, 150000000, 120000000], dtype=np.int64)
//! 
//! bars = rangebar_rust.compute_range_bars(
//!     prices=prices,
//!     volumes=volumes, 
//!     timestamps=timestamps,
//!     threshold_bps=8000  # 0.8% as basis points
//! )
//! ```

use pyo3::prelude::*;
use pyo3::types::PyDict;
use numpy::{IntoPyArray, PyReadonlyArray1};

mod range_bars;
mod fixed_point;
mod types;

use range_bars::RangeBarProcessor;
use types::AggTrade;
use fixed_point::{FixedPoint, BASIS_POINTS_SCALE};

/// Compute range bars from aggregated trade data
/// 
/// # Arguments
/// 
/// * `prices` - Array of prices as fixed-point integers (scaled by 1e8)
/// * `volumes` - Array of volumes as fixed-point integers (scaled by 1e8)  
/// * `timestamps` - Array of timestamps in milliseconds
/// * `trade_ids` - Array of aggregate trade IDs
/// * `first_ids` - Array of first trade IDs
/// * `last_ids` - Array of last trade IDs
/// * `threshold_bps` - Threshold in basis points (8000 = 0.8%)
/// 
/// # Returns
/// 
/// Dictionary containing arrays of range bar data:
/// - `open_times`: Opening timestamps
/// - `close_times`: Closing timestamps  
/// - `opens`: Opening prices
/// - `highs`: High prices
/// - `lows`: Low prices
/// - `closes`: Closing prices
/// - `volumes`: Total volumes
/// - `turnovers`: Total turnovers (price * volume)
/// - `trade_counts`: Number of trades per bar
/// - `first_ids`: First trade IDs
/// - `last_ids`: Last trade IDs
#[pyfunction]
fn compute_range_bars<'py>(
    py: Python<'py>,
    prices: PyReadonlyArray1<'py, i64>,
    volumes: PyReadonlyArray1<'py, i64>,
    timestamps: PyReadonlyArray1<'py, i64>,
    trade_ids: PyReadonlyArray1<'py, i64>,
    first_ids: PyReadonlyArray1<'py, i64>,
    last_ids: PyReadonlyArray1<'py, i64>,
    threshold_bps: u32,
) -> PyResult<Bound<'py, PyDict>> {
    // Convert input arrays to Rust slices
    let prices = prices.as_slice()?;
    let volumes = volumes.as_slice()?;
    let timestamps = timestamps.as_slice()?;
    let trade_ids = trade_ids.as_slice()?;
    let first_ids = first_ids.as_slice()?;
    let last_ids = last_ids.as_slice()?;
    
    // Validate input lengths
    if !(prices.len() == volumes.len() 
         && volumes.len() == timestamps.len()
         && timestamps.len() == trade_ids.len()
         && trade_ids.len() == first_ids.len()
         && first_ids.len() == last_ids.len()) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "All input arrays must have the same length"
        ));
    }
    
    if prices.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Input arrays cannot be empty"
        ));
    }
    
    // Create aggregated trades vector
    let mut trades = Vec::with_capacity(prices.len());
    for i in 0..prices.len() {
        trades.push(AggTrade {
            agg_trade_id: trade_ids[i],
            price: FixedPoint(prices[i]),
            volume: FixedPoint(volumes[i]),
            first_trade_id: first_ids[i],
            last_trade_id: last_ids[i],
            timestamp: timestamps[i],
        });
    }
    
    // Process range bars (release GIL for performance)
    let bars = py.detach(|| {
        let mut processor = RangeBarProcessor::new(threshold_bps);
        processor.process_trades(&trades)
    })?;
    
    // Convert results to Python arrays
    let len = bars.len();
    let mut open_times = Vec::with_capacity(len);
    let mut close_times = Vec::with_capacity(len);
    let mut opens = Vec::with_capacity(len);
    let mut highs = Vec::with_capacity(len);
    let mut lows = Vec::with_capacity(len);
    let mut closes = Vec::with_capacity(len);
    let mut volumes_out = Vec::with_capacity(len);
    let mut turnovers = Vec::with_capacity(len);
    let mut trade_counts = Vec::with_capacity(len);
    let mut first_ids_out = Vec::with_capacity(len);
    let mut last_ids_out = Vec::with_capacity(len);
    
    for bar in bars {
        open_times.push(bar.open_time);
        close_times.push(bar.close_time);
        opens.push(bar.open.0);
        highs.push(bar.high.0);
        lows.push(bar.low.0);
        closes.push(bar.close.0);
        volumes_out.push(bar.volume.0);
        turnovers.push(bar.turnover);
        trade_counts.push(bar.trade_count);
        first_ids_out.push(bar.first_id);
        last_ids_out.push(bar.last_id);
    }
    
    // Create result dictionary
    let result = PyDict::new(py);
    result.set_item("open_times", open_times.into_pyarray(py))?;
    result.set_item("close_times", close_times.into_pyarray(py))?;
    result.set_item("opens", opens.into_pyarray(py))?;
    result.set_item("highs", highs.into_pyarray(py))?;
    result.set_item("lows", lows.into_pyarray(py))?;
    result.set_item("closes", closes.into_pyarray(py))?;
    result.set_item("volumes", volumes_out.into_pyarray(py))?;
    // Convert i128 to i64 for numpy compatibility (may lose precision for very large values)
    let turnovers_i64: Vec<i64> = turnovers.iter().map(|&x| x as i64).collect();
    result.set_item("turnovers", turnovers_i64.into_pyarray(py))?;
    result.set_item("trade_counts", trade_counts.into_pyarray(py))?;
    result.set_item("first_ids", first_ids_out.into_pyarray(py))?;
    result.set_item("last_ids", last_ids_out.into_pyarray(py))?;
    
    Ok(result)
}

/// Convert price string to fixed-point integer
/// 
/// # Arguments
/// 
/// * `price` - Price as decimal string (e.g., "50000.12345678")
/// 
/// # Returns
/// 
/// Fixed-point integer scaled by 1e8
#[pyfunction]
fn price_to_fixed_point(price: &str) -> PyResult<i64> {
    Ok(FixedPoint::from_str(price)?.0)
}

/// Convert fixed-point integer to price string  
/// 
/// # Arguments
/// 
/// * `fixed_point` - Fixed-point integer scaled by 1e8
/// 
/// # Returns
/// 
/// Price as decimal string
#[pyfunction]
fn fixed_point_to_price(fixed_point: i64) -> String {
    FixedPoint(fixed_point).to_string()
}

/// Compute range bar thresholds for given open price and threshold
/// 
/// # Arguments
/// 
/// * `open_price` - Opening price as fixed-point integer
/// * `threshold_bps` - Threshold in basis points (8000 = 0.8%)
/// 
/// # Returns
/// 
/// Tuple of (upper_threshold, lower_threshold) as fixed-point integers
#[pyfunction]
fn compute_thresholds(open_price: i64, threshold_bps: u32) -> (i64, i64) {
    let open = FixedPoint(open_price);
    let (upper, lower) = open.compute_range_thresholds(threshold_bps);
    (upper.0, lower.0)
}

/// Python module definition
#[pymodule]
fn _rangebar_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_range_bars, m)?)?;
    m.add_function(wrap_pyfunction!(price_to_fixed_point, m)?)?;
    m.add_function(wrap_pyfunction!(fixed_point_to_price, m)?)?;
    m.add_function(wrap_pyfunction!(compute_thresholds, m)?)?;
    
    // Add constants
    m.add("BASIS_POINTS_SCALE", BASIS_POINTS_SCALE)?;
    m.add("FIXED_POINT_SCALE", fixed_point::SCALE)?;
    
    Ok(())
}