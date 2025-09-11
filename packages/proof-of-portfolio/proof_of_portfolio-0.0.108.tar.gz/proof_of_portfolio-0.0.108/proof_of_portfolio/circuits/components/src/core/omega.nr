use crate::utils::constants::{
    ARRAY_SIZE, OMEGA_NOCONFIDENCE_VALUE, SCALE, STATISTICAL_CONFIDENCE_MINIMUM_N,
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

            let scale_factor = 1000000;
            let product_sum_positive_scaled = product_sum_positive / scale_factor;
            let product_sum_negative_scaled = product_sum_negative / scale_factor;

            let positive_cross = product_sum_positive_scaled * sum_weights_negative;
            let negative_cross = product_sum_negative_scaled * sum_weights_positive;

            let abs_negative = if negative_cross >= 0 {
                negative_cross
            } else {
                -negative_cross
            };
            let omega_loss_min_scaled = omega_loss_min / scale_factor;
            let effective_denominator = if abs_negative >= omega_loss_min_scaled {
                abs_negative
            } else {
                omega_loss_min_scaled
            };

            if effective_denominator != 0 {
                positive_cross / effective_denominator
            } else {
                0
            }
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
            positive_sum / effective_denominator
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
    let weights = [0; ARRAY_SIZE];
    let result = omega(returns, 4, weights, false, true, 10000000, 0);
    assert(result == 1);
}

#[test]
fn test_omega_scaling() {
    let mut log_returns = [0; ARRAY_SIZE];
    log_returns[0] = SCALE / 100;
    log_returns[1] = -SCALE / 200;
    let actual_len = 60u32;
    let weights = [100000; ARRAY_SIZE];
    let use_weighting = false;
    let bypass_confidence = true;
    let omega_loss_min = SCALE / 10;
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
    assert(result >= 0);
}

#[test]
fn test_omega_parity() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000000i64;
    returns[1] = -2000000i64;
    returns[2] = 1500000i64;
    let weights = [100000i64; ARRAY_SIZE];
    let result = omega(returns, 3u32, weights, false, true, 10000000i64, 0i64);
    let expected = 0i64;
    assert(result == expected);
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
