use crate::utils::{
    constants::{
        ARRAY_SIZE, DAYS_IN_YEAR,
        RATIO_SCALE_FACTOR, SCALE, SORTINO_DOWNSIDE_MINIMUM, SORTINO_NOCONFIDENCE_VALUE,
        STATISTICAL_CONFIDENCE_MINIMUM_N,
    },
    sqrt::sqrt,
};

pub fn sortino(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    _RISK_FREE_RATE: i64,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    _avg_daily_return: i64,
    _variance_val: i64,
    ann_excess_return_val: i64,
    daily_rf: i64,
) -> i64 {
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SORTINO_NOCONFIDENCE_VALUE
    } else {
        let excess_return = ann_excess_return_val;

        let mut weighted_sum_down: i64 = 0;
        let mut sum_w_down: i64 = 0;
        let mut downside_returns_sum: i64 = 0;
        let mut negative_count: u32 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                if log_returns[i] < daily_rf {
                    downside_returns_sum += log_returns[i];
                    negative_count += 1;
                    if use_weighting {
                        weighted_sum_down += log_returns[i] * weights[i];
                        sum_w_down += weights[i];
                    }
                }
            }
        }

        if negative_count > 0 {
            let downside_mean = if use_weighting {
                if sum_w_down != 0 {
                    weighted_sum_down / sum_w_down
                } else {
                    0
                }
            } else {
                downside_returns_sum / (negative_count as i64)
            };

            let downside_variance_pre = if use_weighting {
                let mut weighted_sum_sq_diff: i64 = 0;
                for i in 0..ARRAY_SIZE {
                    if (i as u32) < actual_len {
                        if log_returns[i] < daily_rf {
                            let diff = log_returns[i] - downside_mean;
                            let sq_diff = diff * diff;
                            let scaled_sq_diff = sq_diff / SCALE;
                            weighted_sum_sq_diff += scaled_sq_diff * weights[i];
                        }
                    }
                }
                if sum_w_down != 0 {
                    weighted_sum_sq_diff / sum_w_down
                } else {
                    0
                }
            } else {
                let mut sum_sq_diff: i64 = 0;
                for i in 0..ARRAY_SIZE {
                    if (i as u32) < actual_len {
                        if log_returns[i] < daily_rf {
                            let diff = log_returns[i] - downside_mean;
                            let sq_diff = diff * diff;
                            let scaled_sq_diff = sq_diff / SCALE;
                            sum_sq_diff += scaled_sq_diff;
                        }
                    }
                }
                if negative_count > 0 {
                    sum_sq_diff / (negative_count as i64)
                } else {
                    0
                }
            };

            let annualized_variance = downside_variance_pre * (DAYS_IN_YEAR as i64);
            let downside_volatility = sqrt(annualized_variance as u64) as i64;

            let effective_downside_volatility = if downside_volatility > SORTINO_DOWNSIDE_MINIMUM {
                downside_volatility
            } else {
                SORTINO_DOWNSIDE_MINIMUM
            };

            (excess_return * RATIO_SCALE_FACTOR) / effective_downside_volatility
        } else {
            (excess_return * RATIO_SCALE_FACTOR) / SORTINO_DOWNSIDE_MINIMUM
        }
    }
}

#[test]
fn test_sortino_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;
    returns[4] = 600;

    let weights = [100000; ARRAY_SIZE];
    let avg = 320;
    let variance_val = 200000;
    let ann_excess = 116700;
    let result = sortino(
        returns,
        5,
        100,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
        0,
    );
    assert(result != 0);
}

#[test]
fn test_sortino_no_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 1000;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 1000;
    let variance_val = 0;
    let ann_excess = 365000;
    let result = sortino(
        returns,
        5,
        100,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
        0,
    );
    assert(result == SORTINO_NOCONFIDENCE_VALUE);
}

#[test]
fn test_sortino_all_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -500;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = -500;
    let variance_val = 0;
    let ann_excess = -182500;
    let result = sortino(
        returns,
        5,
        0,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
        0,
    );
    assert(result != 0);
}

#[test]
fn test_sortino_high_downside_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 2000;
    returns[1] = -1500;
    returns[2] = 1800;
    returns[3] = -1200;
    returns[4] = 1600;

    let weights = [100000; ARRAY_SIZE];
    let avg = 600;
    let variance_val = 450000;
    let ann_excess = 218800;
    let result = sortino(
        returns,
        5,
        200,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
        0,
    );
    assert(result != 0);
}

#[test]
fn test_sortino_scaling() {
    let mut log_returns = [0; ARRAY_SIZE];
    log_returns[0] = SCALE / 100; // 0.01 * SCALE
    log_returns[1] = -SCALE / 200; // -0.005 * SCALE
    let actual_len = 60u32;
    let risk_free_rate = 0;
    let weights = [100000; ARRAY_SIZE];
    let use_weighting = false;
    let bypass_confidence = true;
    let avg_daily_return = SCALE / 36500; // 0.01% daily for 1% annual approx
    let variance_val = 0;
    let ann_excess_return_val = SCALE / 100; // 1%
    let daily_rf = 0;
    let result = sortino(
        log_returns,
        actual_len,
        risk_free_rate,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
        daily_rf,
    );
    assert(result > 0); // scaling test, result should be positive
}
