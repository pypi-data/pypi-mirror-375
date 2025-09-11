use crate::utils::constants::{
    ARRAY_SIZE, OMEGA_NOCONFIDENCE_VALUE, RATIO_SCALE_FACTOR, SCALE,
    STATISTICAL_CONFIDENCE_MINIMUM_N,
};

pub fn omega(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    omega_loss_min: i64,
    _daily_rf: i64,
) -> i64 {
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        OMEGA_NOCONFIDENCE_VALUE
    } else {
        if use_weighting {
            let mut product_sum_positive: i64 = 0;
            let mut product_sum_negative: i64 = 0;
            let mut sum_weights_positive_raw: i64 = 0;
            let mut sum_weights_negative_raw: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let weight = weights[i];
                    let log_return = log_returns[i];
                    if log_return > 0 {
                        product_sum_positive += log_return * weight;
                        sum_weights_positive_raw += weight;
                    } else {
                        product_sum_negative += log_return * weight;
                        sum_weights_negative_raw += weight;
                    }
                }
            }

            // Apply max with omega_loss_min like in Python reference
            let sum_weights_positive = if sum_weights_positive_raw >= omega_loss_min {
                sum_weights_positive_raw
            } else {
                omega_loss_min
            };
            let sum_weights_negative = if sum_weights_negative_raw >= omega_loss_min {
                sum_weights_negative_raw
            } else {
                omega_loss_min
            };

            // Apply cross-multiplication like in PTN reference implementation
            let positive_sum_weighted = product_sum_positive * sum_weights_negative;
            let negative_sum_weighted = product_sum_negative * sum_weights_positive;

            let effective_denominator = if (-negative_sum_weighted) >= omega_loss_min {
                -negative_sum_weighted
            } else {
                omega_loss_min
            };
            (positive_sum_weighted * RATIO_SCALE_FACTOR) / effective_denominator
        } else {
            let mut positive_sum: i64 = 0;
            let mut negative_sum: i64 = 0;
            let mut _count_pos: u32 = 0;
            let mut _count_neg: u32 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let log_return = log_returns[i];
                    if log_return > 0 {
                        positive_sum += log_return;
                    } else {
                        negative_sum += log_return;
                    }
                }
            }

            let effective_denominator = if -negative_sum >= omega_loss_min {
                -negative_sum
            } else {
                omega_loss_min
            };
            (positive_sum * RATIO_SCALE_FACTOR) / effective_denominator
        }
    }
}

#[test]
fn test_omega_all_positive() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false, 10000000, 0);
    assert(result == 0);
}

#[test]
fn test_omega_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false, 10000000, 0);
    assert(result == 0);
}

#[test]
fn test_omega_mixed_returns() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 4, weights, false, false, 10000000, 0);
    assert(result == 0);
}

#[test]
fn test_omega_zero_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 0;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false, 10000000, 0);
    assert(result == 0);
}

#[test]
fn test_omega_ptn_parity() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 10000000;
    returns[1] = -20000000;
    returns[2] = 0;
    returns[3] = 15000000;
    let weights = [0; ARRAY_SIZE]; // not used since unweighted
    let result = omega(returns, 4, weights, false, true, 10000000, 0);
    assert(result == 1250000);
}

#[test]
fn test_omega_scaling() {
    let mut log_returns = [0; ARRAY_SIZE];
    log_returns[0] = SCALE / 100; // 0.01 * SCALE
    log_returns[1] = -SCALE / 200; // -0.005 * SCALE
    let actual_len = 60u32;
    let weights = [100000; ARRAY_SIZE];
    let use_weighting = false;
    let bypass_confidence = true;
    let omega_loss_min = SCALE / 10; // 0.1 * SCALE
    let daily_rf = 0;
    let result = omega(
        log_returns,
        actual_len,
        weights,
        use_weighting,
        bypass_confidence,
        omega_loss_min,
        daily_rf,
    );
    assert(result > 0); // scaling test, result should be positive
}

#[test]
fn test_omega_parity() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000000i64; // 0.01 * SCALE
    returns[1] = -2000000i64; // -0.02 * SCALE
    returns[2] = 1500000i64; // 0.015 * SCALE
    let weights = [100000i64; ARRAY_SIZE];
    let result = omega(
        returns,
        3u32,
        weights,
        false,
        true,
        10000000i64, // 0.1 * SCALE
        0i64,
    );
    let expected = 250000i64;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff < 1000);
}

#[test]
fn test_omega_less_than_60_days() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000000i64;
    let weights = [100000i64; ARRAY_SIZE];
    let result = omega(returns, 59u32, weights, false, false, 10000000i64, 0i64);
    assert(result == 0i64);
}

#[test]
fn test_omega_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    let weights = [100000i64; ARRAY_SIZE];
    let result = omega(returns, 60u32, weights, false, true, 10000000i64, 0i64);
    assert(result == 0i64);
}
