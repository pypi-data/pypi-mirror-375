use crate::utils::constants::{
    ARRAY_SIZE, LARGE_POSITIVE_VALUE, OMEGA_LOSS_MINIMUM, OMEGA_NOCONFIDENCE_VALUE,
    OMEGA_SCALE_FACTOR, RATIO_SCALE_FACTOR, STATISTICAL_CONFIDENCE_MINIMUM_N,
};

pub fn omega(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    weights: [i64; ARRAY_SIZE],
    use_weighting: bool,
    bypass_confidence: bool,
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

            if sum_weights_positive == 0 {
                sum_weights_positive = OMEGA_LOSS_MINIMUM;
            }
            if sum_weights_negative == 0 {
                sum_weights_negative = OMEGA_LOSS_MINIMUM;
            }

            let positive_sum_u128 = (product_sum_positive as u128) * (sum_weights_negative as u128);
            let negative_sum_u128 = ((-product_sum_negative) as u128) * (sum_weights_positive as u128);

            let positive_sum = (positive_sum_u128 / 1000000) as i64;
            let negative_sum = (negative_sum_u128 / 1000000) as i64;

            let effective_denominator = if negative_sum >= OMEGA_LOSS_MINIMUM {
                negative_sum
            } else {
                OMEGA_LOSS_MINIMUM
            };
            ((positive_sum * RATIO_SCALE_FACTOR) / effective_denominator) as i64
        } else {
            let mut positive_sum: u64 = 0;
            let mut negative_sum: u64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    if log_returns[i] > 0 {
                        positive_sum = positive_sum + (log_returns[i] as u64);
                    } else if log_returns[i] < 0 {
                        negative_sum = negative_sum + ((-log_returns[i]) as u64);
                    }
                }
            }

            let effective_denominator = if negative_sum >= OMEGA_LOSS_MINIMUM as u64 {
                negative_sum
            } else {
                OMEGA_LOSS_MINIMUM as u64
            };
            ((positive_sum * RATIO_SCALE_FACTOR as u64) / effective_denominator) as i64
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
    let result = omega(returns, 5, weights, false, false);
    assert(result == 10000000);
}

#[test]
fn test_omega_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false);
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
    let result = omega(returns, 4, weights, false, false);
    assert(result == 22500000);
}

#[test]
fn test_omega_zero_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 0;
    }

    let weights = [100000; ARRAY_SIZE];
    let result = omega(returns, 5, weights, false, false);
    assert(result == 10000000);
}
