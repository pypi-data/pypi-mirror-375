use crate::utils::{
    constants::{
        ARRAY_SIZE, RATIO_SCALE_FACTOR, SCALE,
        SHARPE_STDDEV_MINIMUM, STATISTICAL_CONFIDENCE_MINIMUM_N, SHARPE_NOCONFIDENCE_VALUE,
    },
    sqrt::sqrt,
};

pub fn sharpe(
    _daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    _risk_free_rate: i64,
    _weights: [i64; ARRAY_SIZE],
    _use_weighting: bool,
    bypass_confidence: bool,
    _avg_daily_return: i64,
    variance_val: i64,
    ann_excess_return_val: i64,
    noconfidence_value: i64,
) -> i64 {
    let result = if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        noconfidence_value
    } else {
        let excess_return = ann_excess_return_val;
        let volatility = if actual_len < 2 {
            SCALE
        } else {
            let annualized_variance = variance_val * 365;
            sqrt(annualized_variance as u64) as i64
        };
        let effective_volatility = if volatility < SHARPE_STDDEV_MINIMUM {
            SHARPE_STDDEV_MINIMUM
        } else {
            volatility
        };

        (excess_return * RATIO_SCALE_FACTOR) / effective_volatility
    };
    result
}

#[test]
fn test_sharpe_normal_case() {
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
    let result = sharpe(
        returns,
        5,
        100,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess,
        SHARPE_NOCONFIDENCE_VALUE,
    );
    assert(result != 0);
}

#[test]
fn test_sharpe_low_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 50;
    }

    let weights = [100000; ARRAY_SIZE];
    let avg = 50;
    let variance_val = 0;
    let ann_excess = 18240;
    let result = sharpe(
        returns,
        10,
        10,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess, SHARPE_NOCONFIDENCE_VALUE,
    );
    assert(result == SHARPE_NOCONFIDENCE_VALUE);
}

#[test]
fn test_sharpe_high_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 5000;
    returns[1] = -4000;
    returns[2] = 3000;
    returns[3] = -2000;
    returns[4] = 1000;

    let weights = [100000; ARRAY_SIZE];
    let avg = 600;
    let variance_val = 8400000;
    let ann_excess = 218800;
    let result = sharpe(
        returns,
        5,
        200,
        weights,
        false,
        false,
        avg,
        variance_val,
        ann_excess, SHARPE_NOCONFIDENCE_VALUE,
    );
    assert(result != 0);
}

#[test]
fn test_sharpe_scaling() {
    let mut daily_returns = [0; ARRAY_SIZE];
    daily_returns[0] = SCALE / 100; // 0.01 * SCALE
    let actual_len = 60u32;
    let risk_free_rate = 0;
    let weights = [100000; ARRAY_SIZE];
    let use_weighting = false;
    let bypass_confidence = true;
    let avg_daily_return = SCALE / 36500; // 0.01% daily for 1% annual approx
    let variance_val = SCALE / 100; // example variance scaled
    let ann_excess_return_val = SCALE / 100; // 1%
    let result = sharpe(
        daily_returns,
        actual_len,
        risk_free_rate,
        weights,
        use_weighting,
        bypass_confidence,
        avg_daily_return,
        variance_val,
        ann_excess_return_val,
        SHARPE_NOCONFIDENCE_VALUE,
    );
    assert(result > 0); // scaling test, result should be positive
}
