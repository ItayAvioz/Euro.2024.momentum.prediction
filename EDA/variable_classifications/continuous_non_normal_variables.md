# Continuous Variables with Non-Normal Distribution

**Total Variables in Group:** 8

## Statistical Properties

| Variable | Data Type | Description | Distribution Characteristics | Transformation Suggestions |
|----------|-----------|-------------|--------------------------|---------------------------|
| index | int64 | Event sequence number | Monotonically increasing, uniform | Log transformation for time series |
| minute | int64 | Minute of the match (0-120+) | Right-skewed, peaks at certain times | Square root or log transformation |
| possession | int64 | Possession sequence number | Discrete, varies by match tempo | Consider as discrete ordinal |
| away_score | int64 | Away team score | Right-skewed, many zeros | Zero-inflated, consider Poisson |
| timestamp | object | Event timestamp | Non-uniform temporal distribution | Convert to seconds, apply transformation |
| visible_area | object | Pitch area coordinates | Array of 10 coordinates | Extract area features, normalize |
| location | object | Event coordinates | Array of [x, y] coordinates | Extract x, y components separately |
| carry | object | Ball carry end location | JSON with end_location array | Extract end coordinates |


## Analysis Notes

- Variables in this group do not follow a normal distribution (Shapiro-Wilk p ≤ 0.05)
- May require transformation or non-parametric tests
- Consider log, square root, or other transformations
- Many are inherently discrete or have natural boundaries
- **Coordinate arrays require special feature extraction**

## Distribution Patterns

### Right-Skewed Variables
- **minute**: Events cluster in certain time periods (Shapiro p < 0.001)
- **away_score**: Most matches have low scores (0-3)
- **possession**: Varies significantly by team style

### Discrete Count Variables
- **index**: Sequential event numbering
- **period**: Limited to 1, 2, and possible extra time
- **match_week**: Tournament progression stages

### Temporal Variables
- **timestamp**: Non-uniform event timing distribution
- **minute**: Non-normal due to event clustering patterns

### Coordinate Arrays (Special Handling Required)
- **visible_area**: Array of 10 coordinates defining visible pitch area
- **location**: [x, y] coordinates on pitch (0-120 x 0-80)
- **carry**: JSON objects containing end_location coordinates

## Coordinate Array Analysis

### visible_area Structure
```
Sample: [82.06, 80.0, 37.47, 80.0, 3.83, 0.0, 115.58, 0.0, 82.06, 80.0]
- 10 coordinates defining visible rectangular area
- Format: [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5] (5 corner points)
- Coverage: 4,271 events with visible area data
```

### location Structure
```
Sample: [60.0, 40.0]
- Simple [x, y] coordinates
- X-axis: 0-120 (pitch length)
- Y-axis: 0-80 (pitch width)
- Coverage: 4,959 events with location data
```

### carry Structure
```
Sample: {'end_location': [30.4, 24.1]}
- JSON object with end_location key
- Contains [x, y] coordinates where carry ended
- Coverage: 1,261 events with carry data
```

## Feature Engineering for Coordinate Arrays

### visible_area Features
- **visible_area_x_min/max**: Horizontal boundaries
- **visible_area_y_min/max**: Vertical boundaries
- **visible_area_size**: Total visible area
- **visible_area_center_x/y**: Center point coordinates

### location Features
- **location_x**: X-coordinate (0-120)
- **location_y**: Y-coordinate (0-80)
- **location_zone**: Pitch zone (defensive/midfield/attacking third)
- **location_side**: Left/center/right channel

### carry Features
- **carry_end_x**: X-coordinate where carry ended
- **carry_end_y**: Y-coordinate where carry ended
- **carry_distance**: Distance of ball carry
- **carry_direction**: Direction of movement

## Recommended Transformations

### Standard Transformations
1. **Log Transformation**: minute, possession
2. **Square Root**: away_score (for count data)
3. **Ordinal Treatment**: period, match_week
4. **Time Conversion**: timestamp (to seconds since match start)

### Coordinate Transformations
1. **Array Parsing**: Extract individual coordinates
2. **Normalization**: Scale coordinates to 0-1 range
3. **Zone Encoding**: Convert coordinates to tactical zones
4. **Distance Metrics**: Calculate distances and angles

## Non-Parametric Alternatives

- Use Spearman correlation instead of Pearson
- Mann-Whitney U tests instead of t-tests
- Kruskal-Wallis instead of ANOVA
- Quantile regression for robust modeling

## EDA Priority

**High Priority**: minute, location, timestamp (momentum analysis)
**Medium Priority**: period, match_week, carry (context analysis)
**Technical Priority**: visible_area (data quality and spatial analysis)
**Low Priority**: index (technical sequence)

---

## Classification Updates (User Corrections)
- **Added**: minute (confirmed non-normal distribution, Shapiro p < 0.001)
- **Added**: timestamp (continuous time variable, moved from nominal)
- **Added**: visible_area (coordinate array - continuous spatial data)
- **Added**: location (coordinate array - continuous spatial data)  
- **Added**: carry (coordinate array - continuous spatial data)
- **Total count updated**: 7 → 11 variables
- **Note**: Coordinate arrays require special feature extraction but are fundamentally continuous 