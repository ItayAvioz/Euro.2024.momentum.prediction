# Categorical Variables with Natural Ordering

**Total Variables in Group:** 5

## Variable Properties

| Variable | Data Type | Description | Ordering Logic | Sample Values |
|----------|-----------|-------------|----------------|---------------|
| period | object | Match period identifier | Temporal sequence | 1, 2, Extra Time, Penalty Shootout |
| match_week | object | Tournament week | Tournament progression | 1, 2, 3, 4, 5, 6, 7 |
| stage | object | Tournament stage | Competition hierarchy | Group Stage, Round of 16, Quarter-finals, Semi-finals, Final |
| match_date | object | Match date | Temporal sequence | 2024-06-14, 2024-06-15, ..., 2024-07-14 |
| kick_off | object | Match start time | Daily time sequence | 15:00:00.000, 18:00:00.000, 21:00:00.000 |

## Analysis Notes

- Variables with natural ordering (can be ranked)
- Can use rank-based correlation measures
- Suitable for ordinal regression analysis
- Preserve ordering when encoding for models

## Ordering Logic

### Temporal Ordering
- **period**: 1 → 2 → Extra Time → Penalty Shootout
- **minute**: 0 → 1 → 2 → ... → 90 → 90+1 → ...
- **match_week**: Tournament progression from week 1 to final
- **match_date**: Chronological order throughout tournament
- **kick_off**: Daily time progression (afternoon → evening → night)

### Hierarchical Ordering
- **stage**: Group Stage → Round of 16 → Quarter-finals → Semi-finals → Final

## Statistical Analysis Approaches

### Appropriate Tests
- Spearman's rank correlation
- Kendall's tau correlation
- Mann-Whitney U test
- Kruskal-Wallis test
- Ordinal logistic regression

### Encoding Strategies
1. **Label Encoding**: Preserve natural order (1, 2, 3, ...)
2. **Ordinal Encoding**: Custom mapping respecting hierarchy
3. **Polynomial Features**: For non-linear relationships

## EDA Recommendations

### Priority Analysis
1. **stage**: Critical for tournament momentum analysis
2. **period**: Essential for within-match momentum patterns
3. **minute**: Core temporal variable for event analysis
4. **match_week**: Tournament progression context
5. **match_date**: Tournament timeline analysis
6. **kick_off**: Daily timing effects on performance

### Momentum Analysis Applications
- **Period Effects**: Compare 1st vs 2nd half momentum patterns
- **Stage Progression**: Analyze tactical evolution through tournament
- **Time Dynamics**: Minute-by-minute momentum shifts
- **Tournament Fatigue**: Week-by-week performance changes
- **Date Effects**: Performance changes over tournament duration
- **Kick-off Timing**: Impact of match start time on performance

## Visualization Strategies
- Box plots by ordered categories
- Trend lines across ordinal levels
- Heat maps with proper ordering
- Time series plots for temporal variables

## Modeling Considerations
- Use ordinal regression when these are target variables
- Include as ordered predictors in momentum models
- Consider interaction effects between ordinal variables
- Test for non-linear relationships across ordered levels

---

## Classification Updates (User Corrections)
- **Added**: match_date (chronological ordering)
- **Added**: kick_off (daily time progression)
- **Confirmed**: period and match_week remain ordinal
- **Total count updated**: 4 → 6 variables 