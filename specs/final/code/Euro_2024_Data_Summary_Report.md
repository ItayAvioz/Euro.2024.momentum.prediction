# Euro 2024 Data Documentation Summary Report

## 📊 Analysis Overview

**Generated:** Using comprehensive analysis of all CSV files in the Euro 2024 dataset
**Total Columns Analyzed:** 88 columns across 4 data files
**Documentation File:** `Euro_2024_Data_Documentation.csv`

## 📁 Data Files Analyzed

### 1. **matches_complete.csv** (23 columns)
- **Primary Key:** `match_id`
- **Records:** 51 matches (complete tournament)
- **Key Fields:** Match metadata, scores, teams, venues, referees
- **Data Types:** Mix of JSON objects, integers, strings, and categoricals

### 2. **events_complete.csv** (50 columns)
- **Primary Key:** `event_uuid`
- **Records:** 187,858 events
- **Key Fields:** Game events, player actions, tactical data, timestamps
- **Data Types:** Primarily JSON objects with complex event data

### 3. **lineups_complete.csv** (8 columns)
- **Primary Key:** `player_id + match_id`
- **Records:** 2,589 player-match records
- **Key Fields:** Player positions, jersey numbers, team affiliations
- **Data Types:** Simple integers and strings

### 4. **data_360_complete.csv** (7 columns)
- **Primary Key:** `event_uuid`
- **Records:** 163,521 tracking records
- **Key Fields:** Player positions, visible areas, freeze frames
- **Data Types:** Complex JSON arrays with spatial coordinates

## 🔗 Data Connection Methods

### Primary Connections:
- **matches_complete.csv** ↔ **events_complete.csv**: Use `match_id`
- **matches_complete.csv** ↔ **lineups_complete.csv**: Use `match_id`
- **events_complete.csv** ↔ **data_360_complete.csv**: Use `event_uuid`
- **events_complete.csv** ↔ **lineups_complete.csv**: Use `match_id`, `player_id`, `team_id`

### Connection Examples:
```python
# Join matches with events
matches_events = pd.merge(matches_df, events_df, on='match_id')

# Join events with 360 tracking data
events_360 = pd.merge(events_df, data_360_df, on='event_uuid')

# Get player lineup info for events
events_lineups = pd.merge(events_df, lineups_df, on=['match_id', 'player_id'])
```

## 📈 Data Quality Insights

### Missing Data Patterns:
- **events_complete.csv**: Many columns are event-type specific (e.g., 'shot' only applies to shot events)
- **lineups_complete.csv**: Some position data missing (998 records)
- **data_360_complete.csv**: Complete data available for all tracking events

### Data Types Summary:
- **JSON/Dict Fields:** 67 columns (complex structured data)
- **Integer Fields:** 12 columns (IDs, scores, numbers)
- **String/Categorical:** 9 columns (names, timestamps)

## 🎯 Key Fields for Momentum Analysis

### Temporal Data:
- `timestamp`, `minute`, `second` (events_complete.csv)
- `period` (match periods)

### Player Movement:
- `location` (events_complete.csv) - Ball/player coordinates
- `freeze_frame` (data_360_complete.csv) - All player positions
- `visible_area` (data_360_complete.csv) - Tracking coverage

### Game Events:
- `type` - Event types (Pass, Shot, Tackle, etc.)
- `possession_team` - Which team has possession
- `under_pressure` - Pressure situations

### Match Context:
- `match_id`, `team_id`, `player_id` - Entity identifiers
- `stage` - Tournament progression
- `home_score`, `away_score` - Match state

## 📋 Documentation CSV Structure

The generated `Euro_2024_Data_Documentation.csv` contains:

| Column | Description |
|--------|-------------|
| feature_name | Column name from original data |
| source | Source CSV file |
| value_type | Data type classification |
| scale | Measurement scale (Nominal/Interval) |
| data_type | Detailed type description |
| unique_count | Number of unique values |
| measure_unit | Unit of measurement |
| min/max | Range for numeric fields |
| null | Count of missing values |
| notes | Description and connection info |
| top_values | Top 5 values with percentages |
| range | Value range summary |

## 🚀 Next Steps for Momentum Prediction

### Recommended Approach:
1. **Time Windows**: Use minute/second timestamps to create rolling windows
2. **Event Sequences**: Chain events by possession and time proximity  
3. **Spatial Analysis**: Use location data to understand field position impact
4. **Team Dynamics**: Track possession changes and pressure situations
5. **Player Impact**: Connect individual player actions to team momentum

### Key Variables for Y Target:
- Possession changes per time window
- Shot attempts and quality (xG data available)
- Pressure events and defensive actions
- Spatial dominance (field position)
- Score state changes

## 📞 Support

For questions about the data documentation or analysis methodology, refer to:
- Generated documentation: `specs/Euro_2024_Data_Documentation.csv`
- Analysis script: `Data/comprehensive_data_analysis.py`
- This summary: `specs/Euro_2024_Data_Summary_Report.md` 