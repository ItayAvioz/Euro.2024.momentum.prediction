# Euro 2024 Dataset - Variable Classification Summary

**Analysis Date:** December 2024  
**Dataset:** euro_2024_complete_dataset.csv  
**Total Variables:** 59  
**Total Records:** 187,858 events

## Classification Overview

| Variable Type | Count | Percentage | Analysis Priority |
|---------------|-------|------------|-------------------|
| **Continuous Normal** | 3 | 5.1% | High - Standard statistical methods |
| **Continuous Non-Normal** | 8 | 13.6% | High - Requires transformations |
| **Categorical Ordinal** | 5 | 8.5% | High - Natural ordering preserved |
| **Categorical Nominal** | 34 | 57.6% | Medium - Encoding required |
| **Categorical Binomial** | 5 | 8.5% | High - Direct modeling use |

## Relevant Features for Momentum Analysis

### High Priority Variables (Core Analysis)
| Variable | Type | Group | Momentum Application |
|----------|------|-------|---------------------|
| **minute** | Continuous Non-Normal | Temporal | Time-based momentum patterns |
| **period** | Categorical Ordinal | Temporal | Half-time momentum shifts |
| **timestamp** | Continuous Non-Normal | Temporal | Event timing analysis |
| **second** | Continuous Normal | Temporal | Sub-minute precision |
| **location** | Continuous Non-Normal | Spatial | Zone-based momentum |
| **type** | Categorical Nominal | Event | Action-based momentum |
| **event_type** | Categorical Nominal | Event | Simplified event momentum |
| **team** | Categorical Nominal | Team | Team momentum tracking |
| **possession_team** | Categorical Nominal | Team | Possession momentum |
| **under_pressure** | Categorical Binomial | Tactical | Pressure momentum |
| **counterpress** | Categorical Binomial | Tactical | Defensive intensity |
| **play_pattern** | Categorical Nominal | Tactical | Momentum triggers |

### Medium Priority Variables (Context Analysis)
| Variable | Type | Group | Momentum Application |
|----------|------|-------|---------------------|
| **stage** | Categorical Ordinal | Tournament | Competition pressure |
| **match_week** | Categorical Ordinal | Tournament | Tournament progression |
| **match_date** | Categorical Ordinal | Tournament | Timeline effects |
| **player** | Categorical Nominal | Individual | Player impact |
| **position** | Categorical Nominal | Individual | Positional momentum |
| **home_score** | Continuous Normal | Match | Score-based momentum |
| **away_score** | Continuous Non-Normal | Match | Score differential |
| **carry** | Continuous Non-Normal | Spatial | Ball movement patterns |
| **50_50** | Categorical Nominal | Contest | Momentum shifts |
| **out** | Categorical Binomial | Event | Flow interruptions |

### Technical Variables (Support Analysis)
| Variable | Type | Group | Purpose |
|----------|------|-------|---------|
| **match_id** | Categorical Nominal | Identifier | Data joining |
| **id** | Categorical Nominal | Identifier | Event tracking |
| **event_uuid** | Categorical Nominal | Identifier | 360° data linking |
| **visible_area** | Continuous Non-Normal | Quality | Spatial data quality |
| **off_camera** | Categorical Binomial | Quality | Event visibility |

## Detailed Breakdown by Updated Groups

### 1. Continuous Variables with Normal Distribution (3 variables)
**Variables:** duration, second, home_score

**Momentum Applications:**
- **second**: Sub-minute timing precision for momentum changes
- **home_score**: Direct momentum indicator through scoring
- **duration**: Event duration patterns in momentum phases

### 2. Continuous Variables with Non-Normal Distribution (9 variables)
**Variables:** index, period, minute, possession, away_score, match_week, timestamp, visible_area, location, carry

**Key Variables for Momentum:**
- **minute**: Primary temporal variable (non-normal due to event clustering)
- **timestamp**: Precise event timing for momentum sequences
- **location**: Spatial momentum analysis (coordinate arrays)
- **carry**: Ball movement momentum (coordinate arrays)

### 3. Categorical Variables with Natural Ordering (5 variables)
**Variables:** period, minute, match_week, stage, match_date, kick_off

**Momentum Applications:**
- **period**: 1st vs 2nd half momentum patterns
- **stage**: Tournament pressure momentum escalation
- **match_date**: Timeline momentum evolution
- **kick_off**: Daily timing effects on performance

### 4. Categorical Variables without Natural Ordering (36 variables)
**Key Variables:** team, event_type, play_pattern, position, player, home_team_id, away_team_id, 50_50

**Momentum Applications:**
- **team**: Direct momentum tracking by team
- **event_type**: Action-based momentum classification
- **play_pattern**: How momentum-building sequences start
- **50_50**: Contested situations affecting momentum flow

### 5. Binary/Binomial Variables (5 variables)
**Variables:** under_pressure, counterpress, off_camera, injury_stoppage, out, visible_area

**Momentum Applications:**
- **under_pressure**: Defensive pressure as momentum indicator
- **counterpress**: Immediate pressure response patterns
- **out**: Flow interruption affecting momentum
- **injury_stoppage**: Strategic timing momentum breaks

## Coordinate Array Feature Engineering

### Spatial Variables Requiring Special Handling
1. **visible_area**: Extract area boundaries and size
2. **location**: Extract x, y coordinates and tactical zones
3. **carry**: Extract movement vectors and distances

### Feature Extraction Strategy
- Parse coordinate arrays into numerical components
- Create zone-based categorical features
- Calculate spatial relationships and movements
- Normalize coordinates for consistent scaling

## Statistical Analysis Strategy

### Normal Variables (3)
- Standard parametric methods
- Pearson correlations
- Linear regression applications

### Non-Normal Variables (9)
- Transformations before analysis
- Non-parametric statistical tests
- Special handling for coordinate arrays

### Ordinal Variables (5)
- Preserve natural ordering
- Rank-based correlation analysis
- Ordinal regression methods

### Nominal Variables (36)
- Appropriate encoding by cardinality
- Chi-square association tests
- Feature selection post-encoding

### Binary Variables (5)
- Direct use in logistic models
- Binary correlation analysis
- Missing value imputation strategies

## Next Steps for Momentum Analysis

1. **Phase 1**: Focus on high-priority temporal and event variables
2. **Phase 2**: Extract features from coordinate arrays
3. **Phase 3**: Analyze momentum patterns in 3-5 minute windows
4. **Phase 4**: Develop weight functions for momentum persistence
5. **Phase 5**: Advanced pattern recognition and validation

---

## Classification Updates Applied
- **period, match_week**: Confirmed as ordinal
- **50_50, home_team_id, away_team_id**: Moved to nominal (categorical identity)
- **minute, timestamp**: Moved to continuous non-normal
- **visible_area, location, carry**: Added as continuous coordinate arrays
- **out**: Added as binary variable
- **match_date, kick_off**: Added as ordinal variables

**Updated Counts:**
- Continuous Normal: 3 (unchanged)
- Continuous Non-Normal: 7 → 11 (+4)
- Categorical Ordinal: 4 → 6 (+2)
- Categorical Nominal: 37 → 33 (-4)
- Categorical Binomial: 8 → 6 (-2) 