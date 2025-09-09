use components::core::{
    calmar::calmar, drawdown::daily_max_drawdown, omega::omega, sharpe::sharpe, sortino::sortino,
    tstat::statistical_confidence,
};
use components::core::merkle::{
    build_merkle_root, hash_return, hash_signal, merkle_inclusion_check, TradingSignal,
};
use components::utils::{
    ann_excess_return::ann_excess_return,
    average::average,
    constants::{ARRAY_SIZE, MAX_DAYS, MAX_RETURNS, MAX_SIGNALS, MERKLE_DEPTH},
    variance::variance,
};

fn main(
    log_returns: [i64; MAX_DAYS],
    n_returns: u32,
    daily_pnl: [i64; ARRAY_SIZE],
    n_pnl: u32,
    signals: [TradingSignal; MAX_SIGNALS],
    signals_count: u32,
    path_elements: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    path_indices: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    signals_merkle_root: pub Field,
    use_weighting: bool,
    bypass_confidence: pub bool,
    weights: [i64; ARRAY_SIZE],
    calmar_cap: i64,
    days_in_year: i64,
    omega_loss_min: i64,
    annual_risk_free: i64,
    drawdown_max_percent: i64,
) -> pub [Field; 9] {
    // Verify all trading signals are included in the merkle tree
    let mut all_verified = true;
    for i in 0..MAX_SIGNALS {
        if (i as u32) < signals_count {
            let signal_hash = hash_signal(signals[i]);
            let verified = merkle_inclusion_check(
                signal_hash,
                signals_merkle_root,
                path_elements[i],
                path_indices[i],
            );
            all_verified = all_verified & verified;
        }
    }
    assert(all_verified);

    // Build array from returns
    let mut returns_array = [0; ARRAY_SIZE];
    for i in 0..MAX_DAYS {
        if (i as u32) < n_returns {
            returns_array[i] = log_returns[i];
        }
    }

    let weights = if use_weighting {
        weights
    } else {
        // Equal weights when weighting is disabled
        let mut equal_weights = [0; ARRAY_SIZE];
        for i in 0..ARRAY_SIZE {
            equal_weights[i] = 100000; // Scale value for equal weighting
        }
        equal_weights
    };

    let sum_of_weights = if use_weighting {
        let mut sum: i64 = 0;
        for i in 0..ARRAY_SIZE {
            if (i as u32) < n_returns {
                sum += weights[i];
            }
        }
        sum
    } else {
        n_returns as i64
    };

    let avg_daily_return = average(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let variance_val = variance(
        returns_array,
        n_returns,
        1,
        weights,
        use_weighting,
        sum_of_weights,
    );
    let ann_excess_return_val = ann_excess_return(
        returns_array,
        n_returns,
        annual_risk_free,
        weights,
        use_weighting,
        days_in_year,
    );

    let avg_daily_pnl = average(daily_pnl, n_pnl, weights, use_weighting, sum_of_weights);

    let sharpe_ratio = sharpe(
        returns_array,
        n_returns,
        annual_risk_free,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let dmd = daily_max_drawdown(returns_array, n_returns);
    let calmar_ratio = calmar(
        returns_array,
        n_returns,
        annual_risk_free,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
        calmar_cap,
        days_in_year,
        drawdown_max_percent,
    );
    let omega_ratio = omega(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
        omega_loss_min,
    );
    let sortino_ratio = sortino(
        returns_array,
        n_returns,
        annual_risk_free,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );
    let stat_confidence = statistical_confidence(
        returns_array,
        n_returns,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
    );

    let pnl_score_result = avg_daily_pnl;

    // Build merkle root from returns
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < n_returns {
            leaves[i] = hash_return(log_returns[i]);
        }
    }
    let computed_returns_root = build_merkle_root(leaves, n_returns);

    [
        (avg_daily_pnl as u64) as Field,
        (sharpe_ratio as u64) as Field,
        (dmd as u64) as Field,
        (calmar_ratio as u64) as Field,
        (omega_ratio as u64) as Field,
        (sortino_ratio as u64) as Field,
        (stat_confidence as u64) as Field,
        (pnl_score_result as u64) as Field,
        computed_returns_root,
    ]
}
