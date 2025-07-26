# Euro 2024 Nominal Features Analysis Summary

## Overview
Comprehensive analysis of 13 categorical nominal features from the Euro 2024 dataset (187,858 events). This analysis focuses on features with excellent data coverage, excluding those with ~100% missing values.

## Dataset Information
- **Total Events**: 187,858
- **Total Columns**: 59
- **Nominal Features Analyzed**: 13
- **Analysis Date**: Generated from complete Euro 2024 dataset

## Key Findings

### Data Coverage Excellence
- **Perfect Coverage (0% missing)**: 12 out of 13 features
- **Near-Perfect Coverage**: Position (0.46% missing - only 864 events)
- **No features** with significant missing data (all <1% missing)

### Feature Categories by Unique Values

#### High Cardinality (20+ categories)
1. **type** - 33 event types (JSON objects with ID/name)
2. **event_type** - 33 event types (simplified strings)
3. **possession_team** - 24 teams (JSON objects)
4. **team** - 24 teams performing events
5. **home_team_name** - 24 team names
6. **away_team_name** - 24 team names
7. **home_team_id** - 24 numeric team IDs
8. **away_team_id** - 24 numeric team IDs
9. **position** - 24 player positions (JSON objects)

#### Medium Cardinality (10-19 categories)
10. **referee** - 19 match officials (JSON objects)
11. **stadium** - 11 venues (JSON objects)

#### Low Cardinality (2-9 categories)
12. **match_id** - 51 unique matches
13. **play_pattern** - 9 possession start types

## Detailed Feature Analysis

### Event Classification Features

#### Event Types (type & event_type)
- **Most Common**: Pass (53,890 events, 28.69%)
- **Top 3**: Pass (28.69%), Ball Receipt* (27.48%), Carry (23.5%)
- **Distribution**: Well-balanced across different event types
- **Momentum Impact**: Critical for understanding game flow and intensity

#### Play Pattern (9 categories)
- **Most Common**: Regular Play (76,594 events, 40.77%)
- **Top 3**: Regular Play (40.77%), From Throw In (22.29%), From Free Kick (15.86%)
- **Momentum Impact**: Set pieces vs open play affect momentum differently

### Team & Competition Features

#### Team Information (4 related features)
- **Teams**: 24 countries participating in Euro 2024
- **Most Active**: England (15,059-15,599 events), Spain (15,056-15,415), Portugal (12,856-13,199)
- **Data Structure**: 
  - Team names: Simple strings
  - Team objects: JSON with ID/name
  - Team IDs: Numeric identifiers (e.g., 772=Spain, 768=England, 771=France)

#### Match Context
- **Matches**: 51 tournament matches
- **Most Events**: Match 3942349 (5,190 events), Match 3942227 (4,882 events)
- **Distribution**: Fairly even across matches (average ~3,680 events per match)

### Player & Position Features

#### Position (24 categories, 0.46% missing)
- **Most Common**: Left Center Back (19,773 events, 10.57%)
- **Top 3**: Left Center Back (10.57%), Right Center Back (10.05%), Left Defensive Midfield (8.51%)
- **Missing Data**: Only 864 events without position data
- **Momentum Impact**: Different positions have varying momentum contribution

### Infrastructure Features

#### Stadium (11 venues)
- **Most Active**: Signal-Iduna-Park (22,581 events, 12.02%)
- **Top 3**: Signal-Iduna-Park (12.02%), Olympiastadion Berlin (11.16%), Allianz Arena (10.75%)
- **Geographic**: All stadiums in Germany (host country)

#### Referee (19 officials)
- **Most Active**: Daniele Orsato (16,747 events, 8.91%)
- **Top 3**: Orsato (8.91%), Michael Oliver (8.59%), François Letexier (7.86%)
- **Distribution**: Relatively balanced across referees

## Data Quality Assessment

### Strengths
✅ **Excellent Coverage**: 12/13 features with 0% missing data
✅ **Consistent Structure**: JSON objects properly formatted
✅ **Balanced Distribution**: No extreme outliers in category frequencies
✅ **Complete Tournament**: All 24 teams and 51 matches represented
✅ **Rich Context**: Multiple perspectives on same information (team names, IDs, objects)

### Considerations for Modeling
⚠️ **High Cardinality**: Features like team, position, stadium need encoding strategies
⚠️ **JSON Objects**: Complex structures require parsing for ML models
⚠️ **Multiple Representations**: Some information duplicated across features (teams)

## Recommendations for Momentum Modeling

### High Priority Features (Direct Momentum Impact)
1. **event_type**: Primary driver of momentum changes
2. **play_pattern**: Set pieces vs regular play momentum differences
3. **position**: Player role impact on momentum generation
4. **team**: Team-specific momentum patterns

### Medium Priority Features (Contextual Momentum)
5. **home_team_name/away_team_name**: Home advantage and team quality effects
6. **match_id**: Match-specific momentum patterns
7. **referee**: Officiating style impact on game flow

### Low Priority Features (Limited Momentum Impact)
8. **stadium**: Venue effects minimal in neutral tournament
9. **possession_team**: Redundant with team information

### Encoding Strategies
- **One-Hot Encoding**: play_pattern (9 categories)
- **Target Encoding**: team, position (based on momentum outcomes)
- **Frequency Encoding**: event_type (based on rarity/importance)
- **Embedding**: Complex JSON objects if using deep learning

## Files Generated
- **Visualizations**: 13 individual feature analysis charts
- **Summary**: `nominal_features_summary.csv` with complete statistics
- **Location**: `EDA/visualizations/nominal_features/`

## Next Steps
1. **Feature Engineering**: Create momentum-relevant encodings
2. **Correlation Analysis**: Check relationships between nominal features
3. **Temporal Analysis**: How nominal features change over match time
4. **Integration**: Combine with ordinal and continuous features for complete momentum model

---

**Analysis Complete**: All 13 nominal features successfully analyzed with excellent data coverage (≥99.5% for all features). Ready for momentum prediction modeling integration. 