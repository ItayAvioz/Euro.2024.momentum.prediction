# 360° Data Processing Input-Output Examples

## Overview
This document demonstrates how to process StatsBomb 360° freeze frame data to extract spatial insights for soccer analysis and commentary generation.

## 1. Raw 360° Data Input Structure

### Input Format
```json
{
  "event_uuid": "12345678-1234-5678-9012-123456789abc",
  "visible_area": [0, 0, 120, 80],
  "freeze_frame": [
    {"player_id": 1003, "position": [112.3, 39.4], "teammate": true},
    {"player_id": 1002, "position": [88.5, 35.7], "teammate": true},
    {"player_id": 2003, "position": [108.9, 38.7], "teammate": false},
    {"player_id": 2004, "position": [115.2, 35.1], "teammate": false}
  ]
}
```

### Output Summary
- **Total Players**: 6 (3 teammates, 3 opponents)
- **Field Coordinates**: 120m × 80m pitch
- **Player Positions**: [x, y] coordinates in meters

## 2. Freeze Frame Parsing

### Input
Raw freeze frame array with mixed teammate/opponent data

### Processing
```python
def parse_freeze_frame(freeze_frame_data):
    teammates = []
    opponents = []
    
    for player in freeze_frame_data:
        player_info = {
            'id': player['player_id'],
            'x': player['position'][0],
            'y': player['position'][1]
        }
        
        if player['teammate']:
            teammates.append(player_info)
        else:
            opponents.append(player_info)
    
    return teammates, opponents
```

### Output
```
Teammates (3):
  ID 1003: (112.3, 39.4)  # Kane
  ID 1002: (88.5, 35.7)   # Bellingham
  ID 1001: (75.2, 42.1)   # England midfielder

Opponents (3):
  ID 2003: (108.9, 38.7)  # Close defender
  ID 2004: (115.2, 35.1)  # Very close defender
  ID 2001: (95.4, 48.3)   # Distant player
```

## 3. Pressure Calculation

### Input
- **Event Location**: [112.3, 39.4] (Kane's shot position)
- **Pressure Radius**: 5.0m
- **Opponents to Check**: 3 players

### Processing Method
```python
def calculate_pressure(event_location, opponents, radius=5.0):
    event_x, event_y = event_location
    pressure_score = 0
    
    for opponent in opponents:
        distance = sqrt((opponent['x'] - event_x)² + (opponent['y'] - event_y)²)
        
        if distance <= radius:
            pressure_contribution = (radius - distance) / radius
            pressure_score += pressure_contribution
    
    return pressure_score
```

### Output
```
Total pressure score: 0.31
Players applying pressure: 1
  Player 2003: 3.5m away, pressure: 0.31
```

**Interpretation**: Low pressure situation - Kane has space to work with

## 4. Field Zone Analysis

### Input
- **Field Zones**: Defensive (0-40), Midfield (40-80), Attacking (80-120)
- **Player Positions**: All teammates and opponents

### Processing
Counts players in each third of the field and calculates numerical advantages

### Output
```
Defensive Third:
  Teammates: 0, Opponents: 0
  Advantage: Balanced

Midfield Third:
  Teammates: 1, Opponents: 0
  Advantage: Team +1

Attacking Third:
  Teammates: 2, Opponents: 3
  Advantage: Opponents +1
```

**Key Insight**: Netherlands have a 1-player advantage in the attacking third

## 5. Spatial Insights Generation

### Input
- **Pressure Score**: 0.31
- **Event Location**: [112.3, 39.4]
- **Zone Analysis**: Field dominance data

### Processing Logic
```python
def generate_insights(pressure_score, event_location, zone_analysis):
    insights = []
    
    # Pressure analysis
    if pressure_score > 2.0:
        insights.append("High pressure situation")
    elif pressure_score > 1.0:
        insights.append("Moderate pressure")
    else:
        insights.append("Low pressure - space available")
    
    # Location analysis
    x, y = event_location
    if x > 100:
        insights.append("Shot from high-danger penalty area")
    elif x > 80:
        insights.append("Shot from attacking third")
    
    return insights
```

### Output
```
Spatial Insights:
  1. Low pressure - space available
  2. Shot from high-danger penalty area
  3. Outnumbered in attacking third (-1)
```

## 6. Commentary Generation

### Input
All 360° analysis results combined

### Processing
```python
def generate_commentary(event_location, pressure_score, zone_analysis):
    # Location context
    location_desc = "in the penalty area" if x > 100 else "in the attacking third"
    
    # Pressure context
    if pressure_score > 2.0:
        pressure_desc = "under intense pressure"
    elif pressure_score > 1.0:
        pressure_desc = "with defenders closing in"
    else:
        pressure_desc = "with space to work"
    
    # Team context
    attacking_advantage = zone_analysis['attacking']['advantage']
    if attacking_advantage < 0:
        team_context = f"Netherlands have a {abs(attacking_advantage)}-player advantage"
    
    return f"Kane's shot comes from {location_desc}, {pressure_desc}. {team_context}."
```

### Output
```
Generated Commentary:
"Kane's shot comes from in the penalty area, with space to work. 
Spatial analysis shows 0.3 pressure points from nearby defenders. 
Netherlands have a 1-player advantage in the final third."
```

## 7. Complete Processing Pipeline

### Input → Output Flow
1. **Raw freeze frame** → Parse players by team
2. **Player positions** → Calculate defensive pressure
3. **Field zones** → Analyze numerical advantages
4. **Spatial data** → Generate tactical insights
5. **All analysis** → Create natural language commentary

### Key Benefits of 360° Data Processing

| Benefit | Description | Example |
|---------|-------------|---------|
| **Objective Pressure** | Quantifies defensive pressure numerically | 0.31/10 pressure score |
| **Tactical Context** | Identifies numerical advantages by zone | -1 disadvantage in attacking third |
| **Spatial Awareness** | Provides precise positional context | High-danger penalty area shot |
| **Enhanced Commentary** | Adds tactical depth to descriptions | "with space to work" vs "under pressure" |
| **Momentum Support** | Feeds spatial features into ML models | Pressure as momentum predictor |
| **Real-time Insights** | Enables live tactical analysis | Instant field dominance calculations |

## 8. Integration with Momentum Prediction

### 360° Features for ML Models
- **Pressure Score**: Defensive intensity around event
- **Zone Advantages**: Numerical superiority by field area
- **Spatial Danger**: Event location risk assessment
- **Formation Density**: Player clustering patterns
- **Territorial Control**: Field dominance percentages

### Sample Feature Engineering
```python
# 360° features for momentum model
spatial_features = {
    'pressure_score': 0.31,
    'attacking_advantage': -1,
    'danger_level': 'high',
    'field_control_pct': 45.0,
    'formation_compactness': 0.72
}
```

## 9. Real-World Applications

### Use Cases
1. **Live Match Analysis**: Real-time tactical insights
2. **Post-Match Review**: Detailed spatial breakdowns
3. **Player Performance**: Pressure-adjusted metrics
4. **Tactical Preparation**: Opposition analysis
5. **Fan Engagement**: Enhanced commentary and visualizations

### Technical Implementation
- **Data Source**: StatsBomb 360° API
- **Processing**: Python with NumPy for calculations
- **Storage**: Structured spatial features
- **Integration**: ML pipelines and NLP systems
- **Output**: Commentary, visualizations, statistics

## Conclusion

360° data processing transforms raw spatial coordinates into actionable tactical insights. By quantifying pressure, analyzing field zones, and generating contextual commentary, this approach provides the spatial intelligence needed for advanced soccer analysis and momentum prediction.

The demonstrated pipeline shows how rule-based processing can effectively extract meaningful patterns from complex positional data, supporting both automated analysis and human understanding of the game's spatial dynamics. 