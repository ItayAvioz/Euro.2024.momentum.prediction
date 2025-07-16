# Categorical Variables without Natural Ordering

**Total Variables in Group:** 38

## Variable Properties

| Variable | Data Type | Unique Count (Est.) | Sample Values | Description |
|----------|-----------|-------------------|---------------|-------------|
| id | object | ~187K | UUID strings | Unique event identifiers |
| event_uuid | object | ~163K | UUID strings | 360-degree data linking |
| type | object | ~35 | Pass, Shot, Dribble | Event type classifications |
| possession_team | object | 24 | Netherlands, England | Team in possession |
| play_pattern | object | 9 | Regular Play, Free Kick | How play started |
| team | object | 24 | Spain, Germany | Team performing event |
| home_team_name | object | 24 | Netherlands, Spain | Home team identifiers |
| away_team_name | object | 24 | England, France | Away team identifiers |
| home_team_id | object | 24 | 941, 768, 772 | Home team ID numbers |
| away_team_id | object | 24 | 941, 768, 772 | Away team ID numbers |
| 50_50 | object | 2 | True, False | Contested ball situations |
| tactics | object | ~100 | Formation data | Tactical formations |
| related_events | object | ~50K | Event UUID arrays | Connected events |
| player | object | ~500 | Player name/ID objects | Player identifiers |
| position | object | ~25 | Center Forward, Left Back | Player positions |
| pass | object | ~5K | Pass detail objects | Pass characteristics |
| ball_receipt | object | ~1K | Receipt detail objects | Ball reception data |
| dribble | object | ~500 | Dribble detail objects | Dribble attempt details |
| interception | object | ~300 | Interception objects | Interception outcomes |
| duel | object | ~800 | Duel detail objects | Player duel information |
| goalkeeper | object | ~200 | GK action objects | Goalkeeper actions |
| clearance | object | ~400 | Clearance objects | Defensive clearances |
| foul_committed | object | ~600 | Foul detail objects | Foul information |
| foul_won | object | ~600 | Foul won objects | Fouls drawn |
| shot | object | ~800 | Shot detail objects | Shot characteristics |
| block | object | ~200 | Block detail objects | Shot/pass blocks |
| substitution | object | ~300 | Sub detail objects | Player substitutions |
| bad_behaviour | object | ~50 | Card detail objects | Cards and misconduct |
| match_id | object | 51 | Match identifiers | Unique match IDs |
| event_type | object | ~35 | Pass, Shot, Dribble | Simplified event types |
| ball_recovery | object | ~500 | Recovery objects | Ball recovery details |
| miscontrol | object | ~300 | Miscontrol objects | Ball miscontrol events |
| player_off | object | ~300 | Player off objects | Player leaving pitch |
| freeze_frame | object | ~800 | Frame data arrays | Shot freeze frames |
| stadium | object | 10 | Stadium objects | Venue information |
| referee | object | ~20 | Referee objects | Match officials |
| home_lineup | object | 51 | Lineup arrays | Home team lineups |
| away_lineup | object | 51 | Lineup arrays | Away team lineups |

## Analysis Notes

- Variables without natural ordering
- Require dummy encoding for modeling
- Use chi-square tests for associations
- High cardinality variables need special handling

## Variable Categories

### Identifiers (High Cardinality)
- **id, event_uuid**: Unique identifiers (187K+ unique values)
- **match_id**: Match identifiers (51 unique)
- **player**: Player identifiers (~500 unique)

### Event Details (Medium Cardinality)  
- **type, event_type**: Event classifications (~35 types)
- **position**: Player positions (~25 positions)
- **Complex objects**: pass, shot, dribble, etc. (varying structures)

### Teams & Competition (Low Cardinality)
- **Team names**: home_team_name, away_team_name, team (24 teams)
- **Team IDs**: home_team_id, away_team_id (24 unique IDs each)
- **possession_team**: Team in possession (24 teams)
- **play_pattern**: How possession started (9 patterns)

### Match Context (Low Cardinality)
- **50_50**: Contested ball situations (binary nominal)
- **stadium**: Venues (10 stadiums)
- **referee**: Match officials (~20 referees)

### Complex Objects (JSON-like)
- **location**: [x, y] coordinate arrays
- **tactics**: Formation and tactical data
- **freeze_frame**: Shot situation snapshots
- **lineups**: Team composition data

## Encoding Strategies

### One-Hot Encoding (Low Cardinality)
- team, possession_team, play_pattern
- 50_50, stadium, referee
- home_team_id, away_team_id

### Target/Frequency Encoding (High Cardinality)
- player (encode by performance metrics)
- event_type (encode by frequency or importance)
- position (encode by tactical importance)

### Embedding (Very High Cardinality)
- id, event_uuid (if used in deep learning)
- Complex objects (if patterns are important)

## EDA Recommendations

### Priority for Momentum Analysis
1. **High Priority**: team, event_type, play_pattern, position
2. **Medium Priority**: player, home_team_id, away_team_id, stadium
3. **Low Priority**: Complex objects (pass, shot details)
4. **Technical**: id, event_uuid (for joining data)

### Association Analysis
- Chi-square tests between categorical variables
- Cramer's V for effect size measurement
- Mutual information for non-linear relationships

### Visualization Strategies
- Bar charts for frequency distributions
- Mosaic plots for two-way associations
- Heat maps for multi-category relationships
- Network graphs for complex relationships

## Modeling Considerations
- Use appropriate encoding based on cardinality
- Consider target encoding for high-cardinality variables
- Test for multicollinearity after encoding
- Feature selection to manage dimensionality
- Consider clustering similar categories

---

## Classification Updates (User Corrections)
- **Added**: home_team_id (nominal, not binomial - represents team identity, not binary choice)
- **Added**: away_team_id (nominal, not binomial - represents team identity, not binary choice)
- **Added**: 50_50 (nominal, not binomial - while binary, it's a categorical event type)
- **Removed**: match_date, kick_off (moved to ordinal)
- **Note**: Team IDs are nominal because they represent categorical team identity, not binary states 