use crate::utils::constants::SCALE;

pub fn mdd_augmentation(drawdown_decimal: i64) -> i64 {
    let drawdown_factor = SCALE - drawdown_decimal;

    if (drawdown_factor <= 0) | (drawdown_factor > SCALE) {
        0
    } else {
        let drawdown_percentage = ((SCALE - drawdown_factor) * 100) / SCALE;
        let max_drawdown_percentage = 10;

        if drawdown_percentage >= max_drawdown_percentage {
            0
        } else if drawdown_percentage <= 0 {
            0
        } else {
            SCALE / drawdown_percentage
        }
    }
}

pub fn risk_normalization(drawdown_decimal: i64) -> i64 {
    mdd_augmentation(drawdown_decimal)
}

#[test]
fn test_risk_normalization_zero_drawdown() {
    let result = risk_normalization(0);
    assert(result == 0);
}

#[test]
fn test_risk_normalization_high_drawdown() {
    let drawdown_15_percent = (15 * SCALE) / 100;
    let result = risk_normalization(drawdown_15_percent);
    assert(result == 0);
}

#[test]
fn test_risk_normalization_low_drawdown() {
    let drawdown_2_percent = (2 * SCALE) / 100;
    let result = risk_normalization(drawdown_2_percent);
    let expected = SCALE / 2;
    assert(result == expected);
}

#[test]
fn test_risk_normalization_max_threshold() {
    let drawdown_10_percent = (10 * SCALE) / 100;
    let result = risk_normalization(drawdown_10_percent);
    assert(result == 0);
}
