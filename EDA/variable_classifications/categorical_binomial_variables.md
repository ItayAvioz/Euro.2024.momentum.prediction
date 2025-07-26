# Binary/Binomial Variables (True/False with possible missing values)

**Total Variables in Group:** 5

## Variable Properties

| Variable | Data Type | Description | True/False Meaning | Missing Values | Usage |
|----------|-----------|-------------|-------------------|----------------|-------|
| under_pressure | object | Player under defensive pressure | True = pressure applied | Yes | Tactical analysis |
| counterpress | object | Immediate pressure after losing ball | True = counterpress active | Yes | Defensive intensity |
| off_camera | object | Event occurred off camera | True = not visible | Yes | Data quality flag |
| injury_stoppage | object | Event during injury time | True = stoppage time | Yes | Match timing |
| out | object | Ball out of bounds | True = ball is out | Yes | Ball state indicator |

## Analysis Notes

- Binary variables (True/False, 0/1, Yes/No)
- Missing values are still considered binomial variables
- Can be used directly in logistic regression
- Consider imputation strategies for missing values

## Missing Value Patterns

### High Missing Rate (>80%)
- **counterpress**: Missing when not applicable
- **off_camera**: Missing when event is visible
- **injury_stoppage**: Missing during regular time
- **out**: Missing when ball is in play

### Medium Missing Rate (20-80%)
- **under_pressure**: Context-dependent
- **visible_area**: Technical limitation

## Imputation Strategies

### Domain Knowledge Imputation
- **injury_stoppage**: False when missing (default = regular time)
- **off_camera**: False when missing (default = visible)
- **counterpress**: False when missing (default = no counterpress)
- **out**: False when missing (default = ball in play)

### Predictive Imputation
- **under_pressure**: Use event type, player position, and location
- **visible_area**: Use camera coverage patterns

## Statistical Analysis

### Appropriate Tests
- Chi-square test for independence
- Fisher's exact test (small samples)
- McNemar's test (paired data)
- Logistic regression
- Phi coefficient for correlation

### Effect Size Measures
- Odds ratios
- Cohen's d for group differences
- Phi coefficient (binary correlation)

## EDA Applications

### Momentum Analysis Priority
1. **High Priority**: under_pressure, counterpress
2. **Medium Priority**: out, injury_stoppage
3. **Low Priority**: off_camera, visible_area (data quality)

### Key Research Questions
- Does **under_pressure** affect event success rates?
- How does **counterpress** relate to momentum shifts?
- Do **out** events predict possession changes?
- Is **injury_stoppage** timing strategic?

## Visualization Strategies
- Bar charts for frequency comparisons
- Crosstabs with chi-square statistics
- Mosaic plots for relationships
- Time series of binary events

## Modeling Applications

### Direct Usage
- Include as binary predictors (0/1 encoding)
- Interaction terms with other variables
- Feature engineering (combinations of binary flags)

### Target Variables
- Model probability of pressure situations
- Predict counterpress effectiveness
- Classify out-of-bounds patterns

## Feature Engineering Opportunities

### Temporal Features
- **pressure_sequence**: Consecutive pressure events
- **counterpress_duration**: Length of counterpress periods
- **stoppage_timing**: When injury time occurs
- **out_frequency**: Rate of out-of-bounds events

### Interaction Features
- **pressure_and_counterpress**: Combined defensive intensity
- **visibility_quality**: Data reliability indicators

## Quality Considerations
- **off_camera**: Use for data quality assessment
- **visible_area**: Filter unreliable events
- **Missing patterns**: May indicate event context

## Momentum Modeling Integration
- Binary flags as momentum indicators
- Pressure sequences as momentum predictors
- Out events as momentum interruption markers
- Temporal patterns in binary events

---

## Classification Updates (User Corrections)
- **Added**: out (ball out of bounds - binary state)
- **Removed**: 50_50 (moved to nominal - categorical event type)
- **Removed**: home_team_id, away_team_id (moved to nominal - team identity)
- **Total count updated**: 8 → 6 variables
- **Note**: Focus on true binary states rather than categorical identifiers 