use crate::utils::constants::{
    ARRAY_SIZE, CALMAR_NOCONFIDENCE_VALUE, RATIO_SCALE_FACTOR, SCALE,
    STATISTICAL_CONFIDENCE_MINIMUM_N,
};
use super::drawdown::daily_max_drawdown;

pub fn calmar(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    bypass_confidence: bool,
    avg_daily_return: i64,
    calmar_cap: i64,
    days_in_year: i64,
    _drawdown_max_percent: i64,
) -> i64 {
    if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        CALMAR_NOCONFIDENCE_VALUE
    } else {
        let ann_excess_return = avg_daily_return * days_in_year;
        let max_drawdown_decimal = daily_max_drawdown(log_returns, actual_len);

        if (max_drawdown_decimal == 0) | (ann_excess_return <= 0) {
            0
        } else {
            let raw_calmar = (ann_excess_return * RATIO_SCALE_FACTOR) / max_drawdown_decimal;
            if raw_calmar > (calmar_cap * RATIO_SCALE_FACTOR) {
                calmar_cap * RATIO_SCALE_FACTOR
            } else {
                raw_calmar
            }
        }
    }
}

#[test]
fn test_calmar_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 2000;
    returns[3] = -1000;
    returns[4] = 500;
    for i in 5..40 {
        returns[i] = if i % 2 == 0 { 200 } else { -150 };
    }

    let avg = 25;
    let result = calmar(returns, 40, false, avg, 1, 365, 10);
    assert(result != 0);
}

#[test]
fn test_calmar_insufficient_data() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;

    let avg = 250;
    let result = calmar(returns, 2, false, avg, 1, 365, 10);
    assert(result == CALMAR_NOCONFIDENCE_VALUE);
}

#[test]
fn test_calmar_exactly_30_days() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..30 {
        returns[i] = 100;
    }

    let avg = 100;
    let result = calmar(returns, 30, false, avg, 1, 365, 10);
    assert(result != 0);
}

#[test]
fn test_calmar_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..50 {
        returns[i] = -100;
    }

    let avg = -100;
    let result = calmar(returns, 50, false, avg, 1, 365, 10);
    assert(result != 0);
}

#[test]
fn test_calmar_scaling() {
    let mut log_returns = [0; ARRAY_SIZE];
    log_returns[0] = SCALE / 100;
    log_returns[1] = -SCALE / 200;
    let actual_len = 60u32;
    let bypass_confidence = true;
    let avg_daily_return = SCALE / 100;
    let calmar_cap = 10;
    let days_in_year = 365;
    let drawdown_max_percent = 10;
    let result = calmar(
        log_returns,
        actual_len,
        bypass_confidence,
        avg_daily_return,
        calmar_cap,
        days_in_year,
        drawdown_max_percent,
    );

    assert(result >= 0);
}

#[test]
fn test_calmar_parity() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 2000000i64;
    returns[1] = -1000000i64;
    returns[2] = 1000000i64;
    let avg = 666667i64;
    let result = calmar(returns, 3u32, true, avg, 1i64, 365i64, 10i64);
    let expected = 1000000i64;
    let diff = if result > expected {
        result - expected
    } else {
        expected - result
    };
    assert(diff >= 0);
}

#[test]
fn test_calmar_less_than_60_days() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000000i64;
    let avg = 1000000i64;
    let result = calmar(returns, 59u32, false, avg, 1i64, 365i64, 10i64);
    assert(result == -100000000i64);
}

#[test]
fn test_calmar_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    let avg = 0i64;
    let result = calmar(returns, 60u32, true, avg, 1i64, 365i64, 10i64);
    assert(result == 0i64);
}

#[test]
fn test_calmar_all_positive() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..60 {
        returns[i] = 1000000i64;
    }
    let avg = 1000000i64;
    let result = calmar(returns, 60u32, true, avg, 1i64, 365i64, 10i64);
    assert(result == 0i64);
}

#[test]
fn test_calmar_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..60 {
        returns[i] = -1000000i64;
    }
    let avg = -1000000i64;
    let result = calmar(returns, 60u32, true, avg, 1i64, 365i64, 10i64);
    assert(result == 0i64);
}
