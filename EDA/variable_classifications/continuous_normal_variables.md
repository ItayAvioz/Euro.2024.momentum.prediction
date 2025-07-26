# Continuous Variables with Normal Distribution

**Total Variables in Group:** 3

## Statistical Properties

| Variable | Data Type | Description | Analysis Notes |
|----------|-----------|-------------|----------------|
| duration | float64 | Event duration in seconds | Time-based measurements often follow normal distribution for certain event types |
| second | int64 | Second within the minute (0-59) | Seconds within minutes tend to be uniformly distributed, approximating normal |
| home_score | int64 | Home team score | Goal scores can approximate normal distribution in large samples |

## Analysis Notes

- Variables in this group follow a normal distribution (Shapiro-Wilk p > 0.05)
- Can use parametric statistical tests
- Suitable for correlation analysis, regression modeling
- These variables are good candidates for:
  * Pearson correlation analysis
  * Linear regression models
  * t-tests for group comparisons
  * ANOVA for multiple group analysis

## EDA Recommendations

1. **Duration**: Analyze distribution by event type to understand timing patterns
2. **Second**: Use for temporal analysis within minute intervals
3. **Home_score**: Essential for momentum analysis and match outcome predictions

## Statistical Assumptions Verified

- Normality: Confirmed through Shapiro-Wilk test
- Continuous scale: All variables have meaningful numeric values
- Independence: Observations are independent events
- Linearity: Suitable for linear modeling approaches 