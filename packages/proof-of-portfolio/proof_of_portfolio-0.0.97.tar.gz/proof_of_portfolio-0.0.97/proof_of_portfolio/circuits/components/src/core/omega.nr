use crate::utils::constants::{
    ARRAY_SIZE, OMEGA_NOCONFIDENCE_VALUE, RATIO_SCALE_FACTOR, STATISTICAL_CONFIDENCE_MINIMUM_N,
};

pub fn omega(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
    omega_loss_min: i64,
) -> i64 {
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        OMEGA_NOCONFIDENCE_VALUE
    } else {
        if use_weighting {
            let mut product_sum_positive: i64 = 0;
            let mut product_sum_negative: i64 = 0;
            let mut sum_weights_positive: i64 = 0;
            let mut sum_weights_negative: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let weight = weights[i];
                    let log_return = log_returns[i];
                    if log_return > 0 {
                        product_sum_positive += log_return * weight;
                        sum_weights_positive += weight;
                    } else if log_return < 0 {
                        product_sum_negative += log_return * weight;
                        sum_weights_negative += weight;
                    }
                }
            }

            let mean_pos = if sum_weights_positive != 0 {
                product_sum_positive / sum_weights_positive
            } else {
                0
            };
            let mean_neg = if sum_weights_negative != 0 {
                (-product_sum_negative) / sum_weights_negative
            } else {
                0
            };

            let effective_denominator = if mean_neg >= omega_loss_min {
                mean_neg
            } else {
                omega_loss_min
            };
            (mean_pos * RATIO_SCALE_FACTOR) / effective_denominator
        } else {
            let mut positive_sum: i64 = 0;
            let mut negative_sum: i64 = 0;
            let mut count_pos: u32 = 0;
            let mut count_neg: u32 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    if log_returns[i] > 0 {
                        positive_sum += log_returns[i];
                        count_pos += 1;
                    } else if log_returns[i] < 0 {
                        negative_sum += (-log_returns[i]);
                        count_neg += 1;
                    }
                }
            }

            let mean_pos = if count_pos > 0 {
                positive_sum / (count_pos as i64)
            } else {
                0
            };
            let mean_neg = if count_neg > 0 {
                negative_sum / (count_neg as i64)
            } else {
                0
            };

            let effective_denominator = if mean_neg >= omega_loss_min {
                mean_neg
            } else {
                omega_loss_min
            };
            (mean_pos * RATIO_SCALE_FACTOR) / effective_denominator
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
    let result = omega(returns, 5, weights, false, false, 10000000);
    assert(result == 10000000);
}

#[test]
fn test_omega_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false, 10000000);
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
    let result = omega(returns, 4, weights, false, false, 10000000);
    assert(result == 22500000);
}

#[test]
fn test_omega_zero_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 0;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false, 10000000);
    assert(result == 10000000);
}
